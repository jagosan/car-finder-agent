# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app/frontend

# Install app dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application's source code from the host to the container
COPY . .

# Build the React app for production
RUN npm run build

# Serve the React app with Nginx
FROM nginx:stable-alpine
COPY --from=0 /app/frontend/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
