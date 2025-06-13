import argparse
from apps.rag.retriever import run_rag_pipeline

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

run_rag_pipeline(args.file)
