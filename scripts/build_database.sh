#!/bin/bash

python3 -m preprocess.clean_data
python3 -m embedding.vector_embedding
python3 -m vector_db.build_vector_db
