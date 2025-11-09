# Project16-Team-1
AI Powered GRE Vocabulary Tool

The team is developing an AI-powered GRE vocabulary learning tool that integrates with an existing Flask API providing reinforcement-learning-based hints.
The current focus is on building the front-end locally using HTML/CSS/JavaScript (or React), guided by initial wireframes and a mobile-first design approach.
The team is testing mock data to simulate vocabulary words while setting up the core structure and navigation of the application.  

Project Overview 

The AI-Powered GRE Vocabulary Tool is designed to enhance an existing vocabulary-learning application that supports students preparing for the GRE. 
The current tool already leverages a reinforcement learning (RL) model to provide personalized hints based on learner performance.
Our project builds on this foundation by improving the user interface, expanding multimedia features, and integrating gamification to create a more engaging and effective study experience. 
This project is important because vocabulary mastery is a critical component of GRE success, yet many study tools fail to adapt to diverse learner needs.
By introducing audio pronunciations, curated multimedia hints, and mobile-first responsive design, our solution will provide learners with a more accessible and interactive way to strengthen vocabulary retention. 
For the sponsor, this project delivers significant value by extending the functionality and usability of a working product that has already reached over 100 learners.
Enhancements to UI/UX, gamification, and integration with scalable APIs will make the tool more attractive to a broader audience, while also demonstrating the sponsor’s reinforcement learning engine in a practical, real-world application. Ultimately, the project increases the tool’s potential for growth, adoption, and long-term impact in the education technology space. 


Q Learning API Notes
The state = the current word (like “cursory”).
The actions = which hint to show (dialogue, context, story, or gif).
The reward = the student’s response (correct or incorrect).
The Q-value = how confident the app is that a certain hint will help the user get it right.
Each time a user answers, the app updates its confidence level for that word and hint combination. Over time, it learns patterns, for example:
“Story” hints work best for serendipity, but “Dialogue” works better for cacophony.

Our Formula: Qₙₑw = Qₒld + α × (reward − Qₒld)
Q(s,a)←Q(s,a)+α×(r−Q(s,a)) Qnew​=Qold​+α×(reward+γ×max(Qnext​)−Qold​)
Setting
Meaning
Your Value
Effect
α (alpha)
Learning rate /how quickly it updates Q-values
0.05
Learns slowly, ensuring stability
γ (gamma)
Discount factor / how much it values future rewards
0.8
Keeps room for multi-step learning later
ε (exploration_rate)
Chance to try new hints (explore)
0.2 (20%)
Mostly exploits what works, but still experiments
initial_q_value
Starting confidence for new hints
0.1
Starts neutral (not assuming any hint is best)
rewards.correct
Reward for correct answers
+1.0
Reinforces successful hint types
rewards.incorrect
Reward for wrong answers
−0.5
Slight penalty so poor hints drop slowly
Example 1 – User Gets It Correct
The app shows a “dialogue” hint for the word benevolent.
	•	Qₒld = 0.10
	•	α = 0.05
	•	reward = +1
 Qₙₑw = 0.10 + 0.05 × (1 − 0.10) Qₙₑw = 0.10 + 0.05 × 0.9 Qₙₑw = 0.10 + 0.045 = 0.145
The confidence for “dialogue” goes up slightly. The app learns that this hint works well for benevolent.

We set the values to make the system stable, gradual, and adaptive for real users.
A slow learning rate helps the model learn steadily and not overreact to one wrong or right answer.
Gentle penalties make sure the app doesn’t completely reject a hint type after one mistake.
A 20% exploration rate keeps the system curious, letting it try new hint types sometimes instead of always picking the same one.

GIF is included in the Q-learning model, our front-end forces it to be shown last
On learn-meaning html this forces Gif to be last
const ranked = await getRanked(wordId);   // e.g. ["story","gif","context","dialogue"]
// This forces GIF to the end no matter what the model returns
const texts = ranked.filter(h => h !== 'gif');
const hasGif = ranked.includes('gif');
hintQueue = hasGif ? [...texts, 'gif'] : texts;

Our backend still assigns a q-value for the gif, but the UI will never show it because hintQueue
If ever we need to add it, just replace the 3 lines highlighted above with
hintQueue = ranked.slice();

Step by step commands
Before opening the web pages, we need to start the local Flask server. That’s what connects our frontend to the Q-learning model.
Open 2 terminals 
Terminal 1 
Navigate to file path, example:  cd "/Users/ladymalig/Desktop/Working Code/Code"
Set up: python3 -m pip install flask flask-cors
Start Flask: python3 server.py
You’d see something like this: Running on http://127.0.0.1:5001
Terminal 2
Filepath: cd "/Users/ladymalig/Desktop/Working Code/Code"
Start HTTP server: python3 -m http.server 8000
You’d see: Serving HTTP on :: port 8000

