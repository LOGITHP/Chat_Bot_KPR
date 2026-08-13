# Stage 1: Build Vite React bundle
FROM node:20-alpine AS builder

WORKDIR /app

# Copy the entire frontend workspace
COPY package*.json ./
COPY packages ./packages
COPY apps/admin ./apps/admin

# Install dependencies for the whole workspace
RUN npm install

# Build the admin app
RUN npm run build --workspace=apps/admin

# Stage 2: Serve with lightweight Nginx
FROM nginx:alpine

# Copy built frontend assets to Nginx html directory
COPY --from=builder /app/apps/admin/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY apps/admin/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
