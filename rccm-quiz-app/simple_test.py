import requests
import sys

print("=== ULTRA SYNC Common Department Test ===")

session = requests.Session()

try:
    # Start quiz
    response = session.get("http://127.0.0.1:5007/quiz/共通")
    print(f"Quiz start: HTTP {response.status_code}")
    
    if response.status_code \!= 200:
        print("Failed to start quiz")
        sys.exit(1)
    
    # Answer 10 questions
    answers = ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"]
    
    for i in range(10):
        # Submit answer
        response = session.post("http://127.0.0.1:5007/quiz", data={"answer": answers[i]})
        if response.status_code == 200:
            print(f"Question {i+1}: Answered {answers[i]} - OK")
        else:
            print(f"Question {i+1}: Failed with HTTP {response.status_code}")
            sys.exit(1)
    
    # Check result page
    response = session.get("http://127.0.0.1:5007/result")
    if response.status_code == 200:
        print(f"Result page: HTTP {response.status_code} - OK")
        
        if len(response.text) > 1000:
            print("Result page has content - Test SUCCESSFUL")
            print("=== COMMON DEPARTMENT 10-QUESTION COMPLETION TEST: SUCCESS ===")
        else:
            print("Result content: Invalid")
            sys.exit(1)
    else:
        print(f"Result page failed: HTTP {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
