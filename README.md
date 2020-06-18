# diesel_generators

Model for virtually running diesel generator engines on offshore drilling rigs under different operational parameters.

The program runs virtual diesel generator engines in standard parallel load-sharing mode. Input is the TOTAL_POWER column from
the SQLite DB. DB is not included since the files are recorded under NDA while working in offshore oil and gas drilling.

The model runs engines and performs load-dependent start/stop and high-load start on the generators. By changing the operational parameters
for load limits and start/stop times, different behavior of the engines can be achieved. This results in different CO2 emissions,
fuel consumption, and running hours count.

The results of each simulation are presented with matplotlib.
