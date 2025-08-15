# Etapa de build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
# Use npm ou yarn conforme seu lockfile
RUN npm install

COPY . .

# Gera o build de produção (ajuste para "build" se for vite, create-react-app ou similar)
RUN npm run build

# Etapa de produção - serve estático via nginx
FROM nginx:alpine

# Remove página default do nginx
RUN rm -rf /usr/share/nginx/html/*

# Copia o build gerado
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia um config customizado se necessário (opcional)
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
