import numpy as np

# Parameters
n_states = 5  # e.g., 16 vocabulary words
n_actions = 3  # GIF (0), dialogue (1), text definition (2)
Q_table = np.zeros((n_states, n_actions))
learning_rate = 0.8
discount_factor = 0.95
exploration_prob = 0.2
epochs = 1000

# Simulated environment (replace with actual app logic)
def get_user_response(word_id, hint_type):
    # Simulate user interaction: show hint, get quiz answer
    # In a real app, integrate with your UI (e.g., learn-quiz.html)
    # Return 1 if correct, 0 if incorrect
    # Example: Random for simulation
    return np.random.choice([0, 1], p=[0.3, 0.7])  # 70% chance correct

for epoch in range(epochs):
    current_state = np.random.randint(0, n_states)  # Random word
    done = False
    while not done:
        # Choose action (hint type)
        if np.random.rand() < exploration_prob:
            action = np.random.randint(0, n_actions)  # Random hint
        else:
            action = np.argmax(Q_table[current_state])  # Best hint

        # Simulate showing hint and getting user response
        reward = get_user_response(current_state, action)

        # Next state: move to a new word (random for simplicity)
        next_state = np.random.randint(0, n_states)

        # Update Q-table
        Q_table[current_state, action] += learning_rate * \
            (reward + discount_factor * np.max(Q_table[next_state]) - Q_table[current_state, action])

        # Update state
        current_state = next_state

        # End episode after one word (or continue until mastery)
        done = True

# Print learned Q-table
print("Learned Q-table (GIF, Dialogue, Text Definition):")
print(Q_table)

# Optimal hint for each word
optimal_hints = np.argmax(Q_table, axis=1)
hint_names = ['GIF', 'Dialogue', 'Text Definition']
print("Optimal hint for each word:")
for i in range(n_states):
    print(f"Word {i}: {hint_names[optimal_hints[i]]}")