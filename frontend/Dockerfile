FROM node:20-alpine

WORKDIR /app

# instala deps primeiro (cache)
COPY package*.json ./
RUN npm ci

# copia o restante
COPY . .

EXPOSE 5173

# Vite precisa do --host pra aceitar conexões fora do container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
