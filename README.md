# PickABite


This application uses LLaMA with the 3.1 models ([llama-3.1-70b-versatile, meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo, "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"])
to create mini games based on the alimentary plan of a kid (loaded by the parents).

The games available are:

- Creation of recipes (From the POV of the kid and the parent). Create a meal (as a tamagochi) based on the diet plan of the kid. If the food the kid asks to cook is not compliant with the diet plan of the kid (retrieved using toolhouse memory with MongoDB), the LLM proposes a new dish.
- Memory game: A game that takes the next meal of a kid programmed with respect to the current hour, and extracts an array of ingredients to prepare that meal in order to do a memory game. By dping so, we use LLaMa to teach kids how to cook dishes and remember their meals

The parents can:
- Load the kids infos and alimentary plan (built from a dietologist), and inject it in the memory of the LLM (using Toolhouse)
- Create recipes for a the kid telling the age and the weight of the kid, determining if the kid is underweight, overweight or ok.

Technologies used:

- Streamlit
- Toolhouse
- AI/ML
- Groq
- Langchain


Developers:

- Alessio Chiovelli: Chiovelli.alessio@gmail.com
- Sean Cesare Lazzeri: sea.ces.laz@gmail.com