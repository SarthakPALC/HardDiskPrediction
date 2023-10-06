FROM ubuntu:latest
RUN apt-get update && \
    apt-get install -y python3-pip && \
    apt-get clean
RUN pip3 install \
    tqdm \
    numpy \
    tensorflow \
    keras \
    spektral==1.0.0 \
    scikit-learn \
    seaborn \
    matplotlib \
    pymongo \
    fastapi \
    pydantic \
    pandas \
    joblib \
    uvicorn

WORKDIR /HardDiskPrediction
COPY . /HardDiskPrediction
EXPOSE 8000
CMD ["python3", "api_fetch.py"]
