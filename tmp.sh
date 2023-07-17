for i in {1..100}; do 
    python operations/create_rubbish_in_es.py "test${i}" 200 false fast &
done