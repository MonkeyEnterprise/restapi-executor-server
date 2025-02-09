FROM nginx:latest

# Kopieer de aangepaste configuratie naar NGINX
COPY nginx.conf /etc/nginx/nginx.conf

# Expose poort 6410
EXPOSE 6410

CMD ["nginx", "-g", "daemon off;"]
