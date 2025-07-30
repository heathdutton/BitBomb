FROM alpine:latest

RUN apk add --no-cache python3 py3-pip unzip

WORKDIR /app

COPY bitbomb.py .
COPY tests/test_zipbomb.py .

RUN adduser -D -s /bin/sh testuser
USER testuser

# Create a small test zipbomb (50 files, 0.1MB kernel) for safe Docker testing
RUN python3 bitbomb.py --files 50 --kernel-size 0.1 --output test_zipbomb.zip

CMD ["python3", "test_zipbomb.py"]