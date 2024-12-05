#include <iostream>
#include <libpq-fe.h>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <functional>
#include <queue>
#include <sstream>
#include <random>
#include <regex>
#include <filesystem>
#include <fstream>

// Requiere C++17 para usar std::filesystem

// Clase FastAGMSSketch (sin cambios)
class FastAGMSSketch {
private:
    std::vector<std::vector<int>> sketch;
    std::hash<int> hashFunc;
    int rows, cols;

    int hash(int value, int seed) const {
        std::mt19937 rng(seed);
        rng.seed(seed);
        return (value ^ rng()) % cols;
    }

public:
    FastAGMSSketch() : rows(0), cols(0), sketch(0, std::vector<int>(0, 0)) {}

    FastAGMSSketch(int rows, int cols) : rows(rows), cols(cols), sketch(rows, std::vector<int>(cols, 0)) {}

    void update(int value) {
        for (int i = 0; i < rows; ++i) {
            int col = hash(value, i);
            sketch[i][col] += (value > 0 ? 1 : -1);
        }
    }

    int dotProduct(const FastAGMSSketch &other) const {
        if (rows != other.rows || cols != other.cols) {
            throw std::invalid_argument("Sketch dimensions do not match.");
        }

        int result = 0;
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                result += sketch[i][j] * other.sketch[i][j];
            }
        }
        return result;
    }

    FastAGMSSketch merge(const FastAGMSSketch &other) const {
        if (rows != other.rows || cols != other.cols) {
            throw std::invalid_argument("Sketch dimensions do not match.");
        }

        FastAGMSSketch merged(rows, cols);
        for (int i = 0; i < rows; ++i) {
            for (int j = 0; j < cols; ++j) {
                merged.sketch[i][j] = std::min(std::abs(sketch[i][j]), std::abs(other.sketch[i][j]));
            }
        }
        return merged;
    }
};

// Función para obtener los valores de una tabla y construir un sketch
FastAGMSSketch buildSketchFromTable(PGconn *conn, const std::string &tableName, int rows, int cols) {
    FastAGMSSketch sketch(rows, cols);

    // Cambié la consulta para usar el nombre real de la tabla, no el alias
    // Usando LIMIT 1000 para evitar cargar demasiadas filas
    std::string query = "SELECT DISTINCT * FROM " + tableName + " LIMIT 1000;";
    PGresult *res = PQexec(conn, query.c_str());

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        std::cerr << "Query for table " << tableName << " failed: " << PQerrorMessage(conn) << std::endl;
        PQclear(res);
        // PQfinish(conn);
        throw std::runtime_error("Failed to execute query.");
    }

    int nRows = PQntuples(res);
    std::cout << "Fetched " << nRows << " rows for table " << tableName << std::endl;
    for (int i = 0; i < nRows; ++i) {
        int value = std::stoi(PQgetvalue(res, i, 0));  // Usamos el primer valor de cada fila para actualizar el sketch
        sketch.update(value);
    }

    PQclear(res);
    return sketch;
}

// Función para extraer los nombres reales de las tablas de la consulta SQL
std::vector<std::string> extractTablesFromQuery(const std::string& query) {
    std::vector<std::string> tables;
    std::regex tableRegex(R"(\bFROM\b\s+([a-zA-Z0-9_]+))", std::regex_constants::icase);  // Captura las tablas
    std::smatch match;
    std::string q = query;

    // Extraer tablas de la cláusula FROM
    while (std::regex_search(q, match, tableRegex)) {
        std::string table = match[1].str();
        if (!table.empty()) {
            tables.push_back(table);
        }
        q = match.suffix().str();
    }

    // También buscar en JOINs
    std::regex joinRegex(R"(\bJOIN\b\s+([a-zA-Z0-9_]+))", std::regex_constants::icase);
    q = query;
    while (std::regex_search(q, match, joinRegex)) {
        std::string table = match[1].str();
        if (!table.empty()) {
            tables.push_back(table);
        }
        q = match.suffix().str();
    }

    std::cout << "Extracted tables: ";
    for (const auto &table : tables) {
        std::cout << table << " ";
    }
    std::cout << std::endl;

    return tables;
}

// Función para extraer joins de la consulta SQL
std::vector<std::pair<std::string, std::string>> extractJoinsFromQuery(const std::string& query) {
    std::vector<std::pair<std::string, std::string>> joins;
    std::regex whereRegex(R"((\w+)\.(\w+)\s*=\s*(\w+)\.(\w+))");  // Condición de relación entre tablas en WHERE
    std::smatch match;
    std::string q = query;

    // Buscar relaciones entre tablas en WHERE
    while (std::regex_search(q, match, whereRegex)) {
        joins.push_back({match[1], match[3]});
        q = match.suffix().str();
    }

    // También buscar en JOIN ON
    std::regex joinOnRegex(R"(\bJOIN\b\s+([a-zA-Z0-9_]+).*?\bON\b\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+))", std::regex_constants::icase);
    q = query;
    while (std::regex_search(q, match, joinOnRegex)) {
        joins.push_back({match[2], match[4]});
        q = match.suffix().str();
    }

    std::cout << "Extracted " << joins.size() << " joins from query" << std::endl;

    return joins;
}

// Representar el grafo de joins
struct JoinGraph {
    std::unordered_map<std::string, FastAGMSSketch> tableSketches;
    std::vector<std::pair<std::string, std::string>> joins;  // Lista de joins (tabla_a, table_b)
};

// Función para construir el plan textual
std::string buildJoinPlan(const JoinGraph &graph) {
    std::unordered_map<std::string, std::string> resultNames;
    std::unordered_set<std::string> joinedTables;

    auto cmp = [&graph](const std::pair<std::string, std::string> &a,
                        const std::pair<std::string, std::string> &b) {
        FastAGMSSketch mergedA = graph.tableSketches.at(a.first).merge(graph.tableSketches.at(a.second));
        FastAGMSSketch mergedB = graph.tableSketches.at(b.first).merge(graph.tableSketches.at(b.second));
        return mergedA.dotProduct(mergedA) > mergedB.dotProduct(mergedB);
    };

    std::priority_queue<std::pair<std::string, std::string>,
                        std::vector<std::pair<std::string, std::string>>,
                        decltype(cmp)>
        pq(cmp);

    for (const auto &join : graph.joins) {
        pq.push(join);
    }

    std::string joinPlan;

    if (pq.empty()) {
        std::cout << "No joins to process!" << std::endl;
        return "No joins to process";
    }

    while (!pq.empty()) {
        auto [tableA, tableB] = pq.top();
        pq.pop();

        std::string left = resultNames.count(tableA) ? resultNames[tableA] : tableA;
        std::string right = resultNames.count(tableB) ? resultNames[tableB] : tableB;

        std::string newResult = "(" + left + " ⨝ " + right + ")";
        joinPlan = newResult;

        resultNames[tableA + "_" + tableB] = newResult;
        resultNames[tableA] = newResult;
        resultNames[tableB] = newResult;

        joinedTables.insert(tableA);
        joinedTables.insert(tableB);
    }

    return joinPlan;
}

int main(int argc, char* argv[]) {
    // Verificar que se haya proporcionado el directorio como argumento
    if (argc < 2) {
        std::cerr << "Uso: " << argv[0] << " <directorio_con_sql_files>" << std::endl;
        return 1;
    }

    std::string directoryPath = argv[1];

    // Conectarse a la base de datos
    const char *conninfo = "dbname=job user=postgres password=postgres hostaddr=127.0.0.1 port=5432";
    PGconn *conn = PQconnectdb(conninfo);

    if (PQstatus(conn) != CONNECTION_OK) {
        std::cerr << "Connection to database failed: " << PQerrorMessage(conn) << std::endl;
        PQfinish(conn);
        return 1;
    }
    std::cout << "Connected to PostgreSQL!" << std::endl;

    // Abrir el archivo de salida
    std::ofstream outputFile("compass-resultados.txt");
    if (!outputFile.is_open()) {
        std::cerr << "No se pudo abrir el archivo de salida 'compass-resultados.txt'" << std::endl;
        PQfinish(conn);
        return 1;
    }

    // Iterar sobre los archivos .sql en el directorio
    for (const auto& entry : std::filesystem::directory_iterator(directoryPath)) {
        if (entry.is_regular_file() && entry.path().extension() == ".sql") {
            std::string filePath = entry.path().string();
            std::string fileName = entry.path().filename().string();

            std::cout << "Procesando archivo: " << fileName << std::endl;

            // Leer el contenido del archivo .sql
            std::ifstream sqlFile(filePath);
            if (!sqlFile.is_open()) {
                std::cerr << "No se pudo abrir el archivo: " << filePath << std::endl;
                continue;
            }
            std::stringstream buffer;
            buffer << sqlFile.rdbuf();
            std::string query = buffer.str();

            // Extraer los nombres reales de las tablas
            std::vector<std::string> tables = extractTablesFromQuery(query);

            // Extraer los joins de la consulta
            std::vector<std::pair<std::string, std::string>> joins = extractJoinsFromQuery(query);

            if (joins.empty()) {
                std::cout << "No se encontraron joins en la consulta del archivo: " << fileName << std::endl;
                outputFile << fileName << ", No joins found, 0" << std::endl;
                continue;
            }

            // Generar el grafo de joins y los sketches
            JoinGraph graph;
            graph.joins = joins;

            // Crear un conjunto para evitar construir el sketch de la misma tabla varias veces
            std::unordered_set<std::string> processedTables;

            try {
                for (auto& join : joins) {
                    if (processedTables.find(join.first) == processedTables.end()) {
                        graph.tableSketches[join.first] = buildSketchFromTable(conn, join.first, 100, 500);
                        processedTables.insert(join.first);
                    }
                    if (processedTables.find(join.second) == processedTables.end()) {
                        graph.tableSketches[join.second] = buildSketchFromTable(conn, join.second, 100, 500);
                        processedTables.insert(join.second);
                    }
                }
            } catch (const std::exception& e) {
                std::cerr << "Error al construir sketches para el archivo " << fileName << ": " << e.what() << std::endl;
                outputFile << fileName << ", Error building sketches, " << joins.size() << std::endl;
                continue;
            }

            // Generar el plan de ejecución de joins
            std::string joinPlan;
            try {
                joinPlan = buildJoinPlan(graph);
            } catch (const std::exception& e) {
                std::cerr << "Error al construir el plan de join para el archivo " << fileName << ": " << e.what() << std::endl;
                outputFile << fileName << ", Error building join plan, " << joins.size() << std::endl;
                continue;
            }

            // Escribir los resultados en el archivo de salida
            outputFile << fileName << ", \"" << joinPlan << "\", " << joins.size() << std::endl;
            std::cout << "Plan de join generado para " << fileName << ": " << joinPlan << std::endl;
        }
    }

    // Cerrar el archivo de salida y la conexión a la base de datos
    outputFile.close();
    PQfinish(conn);

    std::cout << "Procesamiento completado. Resultados guardados en 'compass-resultados.txt'" << std::endl;
    return 0;
}
