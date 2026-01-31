from flask import Flask, g

app = Flask(__name__)

@app.route('/')
def test():
    try:
        # Simulate global g access
        x = g.get('something', 'default')
        print(f"g.something: {x}")
        
        # List comprehension using 'g' as loop variable
        y = [g for g in range(3)]
        print(f"List comp: {y}")
        
        return "OK"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    with app.app_context():
        # Set a value in g
        g.something = "value"
        print(test())
