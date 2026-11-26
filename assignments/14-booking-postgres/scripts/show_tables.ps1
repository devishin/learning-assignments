$host.ui.RawUI.WindowTitle = "pgAdmin / PostgreSQL booking"
docker exec booking-postgres-dev psql -U admin -d booking -c "\dt" -c "TABLE users;" -c "TABLE tables;" -c "TABLE bookings;"
Read-Host "Press Enter to close"
