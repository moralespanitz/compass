#include <iostream>
#include <libpq-fe.h>
#include <string>
#include <regex>
#include <stack>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <exception>

// Requiere C++17 para usar std::filesystem

// Función para obtener el plan JSON del join directamente desde PostgreSQL
std::string getJoinPlanJSON(PGconn *conn, const std::string &query) {
    std::string explainQuery = "EXPLAIN (FORMAT JSON) " + query;
    PGresult *res = PQexec(conn, explainQuery.c_str());

    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        std::string errorMsg = "Error al ejecutar la consulta EXPLAIN: " + std::string(PQerrorMessage(conn));
        PQclear(res);
        throw std::runtime_error(errorMsg);
    }

    // Combinar todas las líneas del resultado de EXPLAIN en una sola cadena JSON
    std::string jsonPlan = PQgetvalue(res, 0, 0);
    PQclear(res);
    return jsonPlan;
}

// Estructura para almacenar información del join
struct JoinInfo {
    std::string plan;
    int joinCount;
};

// Función para analizar manualmente el JSON y construir el plan de joins
JoinInfo parseJSONPlan(const std::string &jsonPlan) {
    // Expresiones regulares para detectar los nombres de las tablas y los operadores de join
    std::regex seqScanRegex("\"Relation Name\":\\s*\"(\\w+)\"", std::regex_constants::icase);
    std::regex joinRegex("\"Node Type\":\\s*\"(Merge Join|Nested Loop|Hash Join)\"", std::regex_constants::icase);
    std::smatch match;

    std::stack<std::string> joinStack;
    int numJoins = 0;
    auto begin = jsonPlan.cbegin();
    auto end = jsonPlan.cend();

    // Extraer todas las tablas (Seq Scan) y añadirlas a la pila
    while (std::regex_search(begin, end, match, seqScanRegex)) {
        if (match.size() > 1) {
            joinStack.push(match[1]); // Agregar tabla a la pila
        }
        begin = match.suffix().first;
    }

    // Reiniciar el análisis para procesar los operadores de join
    begin = jsonPlan.cbegin();
    while (std::regex_search(begin, end, match, joinRegex)) {
        if (joinStack.size() >= 2) {
            std::string right = joinStack.top();
            joinStack.pop();
            std::string left = joinStack.top();
            joinStack.pop();
            
            std::string combined = "(" + left + " ⨝ " + right + ")";
            joinStack.push(combined);
            numJoins++; // Incrementar el contador de joins
        }
        begin = match.suffix().first;
    }

    JoinInfo result;
    result.plan = joinStack.empty() ? "Error: No se pudo construir el plan." : joinStack.top();
    result.joinCount = numJoins;
    return result;
}

int main(int argc, char* argv[]) {
    // Verificar que se haya proporcionado el directorio como argumento
    if (argc < 2) {
        std::cerr << "Uso: " << argv[0] << " <directorio_con_sql_files>" << std::endl;
        return 1;
    }

    std::string directoryPath = "./job";

    // Conectarse a la base de datos
    const char *conninfo = "dbname=job user=postgres password=postgres hostaddr=127.0.0.1 port=5432";
    PGconn *conn = PQconnectdb(conninfo);

    if (PQstatus(conn) != CONNECTION_OK) {
        std::cerr << "Conexión fallida: " << PQerrorMessage(conn) << std::endl;
        PQfinish(conn);
        return 1;
    }
    std::cout << "Conexión a PostgreSQL exitosa." << std::endl;

    // Abrir el archivo de salida
    std::ofstream outputFile("./data/postgres-resultados.txt");
    if (!outputFile.is_open()) {
        std::cerr << "No se pudo abrir el archivo de salida 'postgres-resultados.txt'" << std::endl;
        PQfinish(conn);
        return 1;
    }

    // Iterar sobre los archivos .sql en el directorio
    try {
        for (const auto& entry : std::filesystem::directory_iterator(directoryPath)) {
            if (entry.is_regular_file() && entry.path().extension() == ".sql") {
                std::string filePath = entry.path().string();
                std::string fileName = entry.path().filename().string();

                std::cout << "Procesando archivo: " << fileName << std::endl;

                // Leer el contenido del archivo .sql
                std::ifstream sqlFile(filePath);
                if (!sqlFile.is_open()) {
                    std::cerr << "No se pudo abrir el archivo: " << filePath << std::endl;
                    outputFile << fileName << ", \"Error: No se pudo abrir el archivo.\"\n";
                    continue;
                }
                std::stringstream buffer;
                buffer << sqlFile.rdbuf();
                std::string query = buffer.str();

                // Verificar que la consulta no esté vacía
                if (query.empty()) {
                    std::cerr << "El archivo " << fileName << " está vacío." << std::endl;
                    outputFile << fileName << ", \"Error: Consulta vacía.\"\n";
                    continue;
                }

                try {
                    // Obtener el plan JSON
                    std::string jsonPlan = getJoinPlanJSON(conn, query);

                    // Analizar el JSON para construir el plan de joins
                    JoinInfo joinInfo = parseJSONPlan(jsonPlan);
                    std::string formattedPlan = joinInfo.plan;

                    // Reemplazar comillas dobles en el plan para evitar conflictos en el CSV
                    size_t pos = 0;
                    while ((pos = formattedPlan.find("\"", pos)) != std::string::npos) {
                        formattedPlan.replace(pos, 1, "\\\"");
                        pos += 2;
                    }

                    // Escribir los resultados en el archivo de salida
                    outputFile << fileName << ", \"" << formattedPlan << "\", " << joinInfo.joinCount << "\n";
                    std::cout << "Plan de join generado para " << fileName << ": " << formattedPlan 
                             << " (Número de joins: " << joinInfo.joinCount << ")" << std::endl;
                } catch (const std::exception &e) {
                    std::cerr << "Error al procesar el archivo " << fileName << ": " << e.what() << std::endl;
                    outputFile << fileName << ", \"Error: " << e.what() << "\"\n";
                }
            }
        }
    } catch (const std::filesystem::filesystem_error& e) {
        std::cerr << "Error al acceder al sistema de archivos: " << e.what() << std::endl;
        outputFile.close();
        PQfinish(conn);
        return 1;
    }

    // Cerrar el archivo de salida y la conexión a la base de datos
    outputFile.close();
    PQfinish(conn);

    std::cout << "Procesamiento completado. Resultados guardados en 'postgres-resultados.txt'" << std::endl;
    return 0;
}
