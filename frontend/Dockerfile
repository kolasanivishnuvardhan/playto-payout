FROM busybox:1.36

WORKDIR /app

COPY . .

EXPOSE 3000

CMD ["httpd", "-f", "-p", "3000", "-h", "/app"]
