#!/bin/bash

# AI Tutor Application Development Setup Script

set -e

echo "🚀 Setting up AI Tutor Application for development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    print_warning "Redis is not installed. Installing Redis..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install redis
        else
            print_error "Please install Redis manually or install Homebrew first."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y redis-server
    else
        print_error "Please install Redis manually for your operating system."
        exit 1
    fi
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    print_warning "FFmpeg is not installed. Installing FFmpeg..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            print_error "Please install FFmpeg manually or install Homebrew first."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    else
        print_error "Please install FFmpeg manually for your operating system."
        exit 1
    fi
fi

print_status "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

print_status "Activating virtual environment..."
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

print_status "Installing Node.js dependencies..."
npm install
print_success "Node.js dependencies installed"

print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Environment file created from template"
    print_warning "Please edit .env file with your configuration before running the application"
else
    print_status "Environment file already exists"
fi

print_status "Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p frontend/build
print_success "Directories created"

print_status "Initializing database..."
cd backend
python -c "from database.connection import create_tables; create_tables()"
cd ..
print_success "Database initialized"

print_status "Starting Redis server..."
if ! pgrep -x "redis-server" > /dev/null; then
    redis-server --daemonize yes
    print_success "Redis server started"
else
    print_status "Redis server already running"
fi

print_success "Development setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your OpenAI API key and other configuration"
echo "2. Run './start.sh' to start the application"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "🔧 Available commands:"
echo "  ./start.sh          - Start the full application"
echo "  npm start           - Start only the frontend"
echo "  python backend/main.py - Start only the backend"
echo "  redis-cli ping      - Test Redis connection"
echo ""
echo "📚 Documentation:"
echo "  Backend API docs: http://localhost:8000/docs"
echo "  README.md for detailed information"
echo ""
print_success "Happy coding! 🎉"