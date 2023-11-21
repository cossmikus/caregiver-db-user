from datetime import datetime, timezone
import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url, sslmode="disable")


@app.route("/api/user", methods=["POST"])
def create_user():
    data = request.get_json()

    # Extract data from the request
    email = data.get("email")
    given_name = data.get("given_name")
    surname = data.get("surname")
    city = data.get("city")
    phone_number = data.get("phone_number")
    profile_description = data.get("profile_description")
    password = data.get("the_password")

    # Perform INSERT into THE_USER table
    with connection:
        with connection.cursor() as cursor:
            insert_query = """
                INSERT INTO THE_USER 
                (email, given_name, surname, city, phone_number, profile_description, the_password) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING user_id;
            """
            cursor.execute(
                insert_query,
                (
                    email,
                    given_name,
                    surname,
                    city,
                    phone_number,
                    profile_description,
                    password,
                ),
            )
            user_id = cursor.fetchone()[0]

    return jsonify({"user_id": user_id, "message": "User created successfully"}), 201


@app.route("/api/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM THE_USER WHERE user_id = %s;", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return jsonify(user_data)
            else:
                return jsonify({"message": "User not found"}), 404


@app.route("/api/user/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            # Extract data from the request
            data = request.get_json()
            given_name = data.get("given_name")
            surname = data.get("surname")
            city = data.get("city")
            phone_number = data.get("phone_number")
            profile_description = data.get("profile_description")
            password = data.get("the_password")

            # Generate the SET clause for the SQL query dynamically
            set_clause = []
            if given_name is not None:
                set_clause.append(f"given_name = '{given_name}'")
            if surname is not None:
                set_clause.append(f"surname = '{surname}'")
            if city is not None:
                set_clause.append(f"city = '{city}'")
            if phone_number is not None:
                set_clause.append(f"phone_number = '{phone_number}'")
            if profile_description is not None:
                set_clause.append(f"profile_description = '{profile_description}'")
            if password is not None:
                set_clause.append(f"the_password = '{password}'")

            # Perform UPDATE on THE_USER table
            if set_clause:
                update_query = f"""
                    UPDATE THE_USER 
                    SET {', '.join(set_clause)} 
                    WHERE user_id = %s;
                """
                cursor.execute(update_query, (user_id,))
                if cursor.rowcount > 0:
                    return jsonify(
                        {"message": f"User with ID {user_id} updated successfully"}
                    )
                else:
                    return jsonify({"message": "User not found"}), 404
            else:
                return jsonify({"message": "No valid fields provided for update"}), 400


@app.route("/api/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM THE_USER WHERE user_id = %s;", (user_id,))
            if cursor.rowcount > 0:
                return jsonify({"message": "User deleted successfully"})
            else:
                return jsonify({"message": "User not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
