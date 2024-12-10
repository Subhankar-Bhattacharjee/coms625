# Use a base image with GCC and Python pre-installed
FROM ubuntu:latest

# Install necessary packages: gcc, gdb, python3, pip, llvm, clang, graphviz, python3-pydot
RUN apt-get update && apt-get install -y \
    gcc \
    gdb \
    python3 \
    python3-pip \
    llvm \
    clang \
    graphviz \
    python3-pydot \
    && apt-get clean

# Copy your local path to the container
WORKDIR /usr/src/app
COPY . .

# Set the default command to bash
CMD ["/bin/bash"]