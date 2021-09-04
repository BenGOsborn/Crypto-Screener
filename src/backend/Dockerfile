# Build container
FROM python
WORKDIR /usr/app
COPY . .
RUN pip3 install  -r requirements.txt

# Start server
CMD python3 server.py