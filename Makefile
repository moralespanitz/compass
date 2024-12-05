compass:
	g++ -std=c++17 -o compass compass.cpp -I/opt/homebrew/opt/libpq/include -L/opt/homebrew/opt/libpq/lib -lpq && ./compass job