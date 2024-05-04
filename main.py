from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# Number of shoes to display per page
SHOES_PER_PAGE = 20


def get_shoes(offset=0, search_criteria=None, shoes_per_page=SHOES_PER_PAGE):
    # Connect to the PostgreSQL database
    host = 'cf9gid2f6uallg.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com'
    database = 'dahhms38n4qhjp'
    user = 'u1859glbeeviu4'
    password = 'p1459b5fdbad742a7027bb00a122c9f3fb273579ce3d681c8a6b1331e525e5ce8'
    port = 5432

    # Connect to the database
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
    cursor = conn.cursor()

    query = 'SELECT * FROM shoes'
    if search_criteria:
        # Set the trigram similarity threshold
        cursor.execute('SET pg_trgm.similarity_threshold TO 0.2')

        # Construct the query using the % operator for trigram similarity
        query += ' WHERE name ILIKE %s AND NOT picture LIKE %s'
        count_query = 'SELECT COUNT(*) FROM shoes WHERE name ILIKE %s AND NOT picture LIKE %s'
        params = ('%' + search_criteria + '%', 'data%')
    else:
        query += ' WHERE NOT picture LIKE %s'
        count_query = 'SELECT COUNT(*) FROM shoes WHERE NOT picture LIKE %s'
        params = ('data%',)

    # Use LIMIT and OFFSET to implement pagination
    query += ' LIMIT %s OFFSET %s'
    cursor.execute(count_query, params)  # Only need the first two elements of params for count query
    total_shoes = cursor.fetchone()[0]

    params += (shoes_per_page, offset)

    cursor.execute(query, params)
    shoes = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()
    return shoes, total_shoes


@app.route('/')
def index():
    # Get the search criteria and page number from the query parameters
    search_criteria = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    # Calculate the offset based on the page number
    offset = (page - 1) * SHOES_PER_PAGE

    # Retrieve shoes and the total number of shoes for the current search and page
    shoes, total_shoes = get_shoes(offset, search_criteria)

    # Calculate the total number of pages
    total_pages = (total_shoes + SHOES_PER_PAGE - 1) // SHOES_PER_PAGE

    return render_template('index.html', shoes=shoes, search_criteria=search_criteria, page=page,
                           total_pages=total_pages)

