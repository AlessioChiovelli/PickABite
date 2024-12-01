import streamlit as st
import random
import time
from datetime import datetime

class MemoryGame:
    def __init__(self):
        weekday_idx = datetime.today().date().weekday()
        weekday = {
            1 : "monday", 
            2 : "tuesday", 
            3 : "wednesday", 
            4 : "thursday", 
            5 : "friday", 
            6 : "saturday", 
            7 : "sunday", 
        }[weekday_idx]
        self.foods_available = {
            "monday" : ['rice', 'chicken', 'spinach', 'onions', 'garlic', 'lemon', 'tomato', 'olive oil'], 
            "tuesday" : ['pasta', 'zucchini', 'ground beef', 'parmesan cheese', 'garlic', 'basil', 'cherry tomatoes'], 
            "wednesday" : ['potatoes', 'salmon', 'green beans', 'butter', 'rosemary', 'onions', 'carrots'], 
            "thursday" : ['quinoa', 'avocado', 'cucumber', 'chickpeas', 'feta cheese', 'olive oil', 'lemon', 'spinach'], 
            "friday" : ['bread', 'cheese', 'tomatoes', 'lettuce', 'ham', 'mustard', 'cucumbers', 'pickles'], 
            "saturday" : ['pasta', 'eggplant', 'mozzarella', 'basil', 'garlic', 'olive oil', 'tomato sauce'], 
            "sunday" : ['chicken', 'potatoes', 'rosemary', 'garlic', 'carrots', 'broccoli', 'olive oil', 'lemon']
        }
        self.foods = self.foods_available[weekday]
        self.foods = ['rice', 'chicken', 'spinach', 'onions', 'garlic', 'lemon', 'tomato', 'olive oil']
        if 'board' not in st.session_state:
            self.initialize_game()

    def initialize_game(self):
        # Initialize game state in session
        cards = self.foods[:8] * 2
        random.shuffle(cards)
        st.session_state.board = [['' for _ in range(4)] for _ in range(4)]
        card_index = 0
        for i in range(4):
            for j in range(4):
                st.session_state.board[i][j] = cards[card_index]
                card_index += 1
        
        st.session_state.revealed = [[False for _ in range(4)] for _ in range(4)]
        st.session_state.matches_found = 0
        st.session_state.moves = 0
        st.session_state.selected = []
        st.session_state.game_over = False

def handle_click(i, j):
    # Handle card click
    if not st.session_state.revealed[i][j] and len(st.session_state.selected) < 2:
        st.session_state.revealed[i][j] = True
        st.session_state.selected.append((i, j))
        
        if len(st.session_state.selected) == 2:
            st.session_state.moves += 1
            i1, j1 = st.session_state.selected[0]
            i2, j2 = st.session_state.selected[1]
            
            # Check if cards match
            if st.session_state.board[i1][j1] == st.session_state.board[i2][j2]:
                st.session_state.matches_found += 1
                st.session_state.selected = []
            else:
                # Schedule cards to be hidden after a delay
                time.sleep(1)
                st.session_state.revealed[i1][j1] = False
                st.session_state.revealed[i2][j2] = False
                st.session_state.selected = []

def main():

    now = datetime.now()
    meal = "lunch" if now.hour < 12 else "dinner"
    st.title("🎮 Food Memory Game")
    st.header("The ingredients are hidden behind the cards. Find all the matching pairs!")
    st.write(f'''
    All the ingredients created for the game are generated based on your next {meal}''')
    
    # Initialize game if needed
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False

    # Start game button
    if not st.session_state.game_started:
        if st.button("Start New Game"):
            st.session_state.game_started = True
            game = MemoryGame()
            st.rerun()
    else:
        game = MemoryGame()
        
        # Display game stats
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Moves: {st.session_state.moves}")
        with col2:
            st.write(f"Matches found: {st.session_state.matches_found}")

        # Create the game board using a grid of buttons
        for i in range(4):
            cols = st.columns(4)
            for j in range(4):
                with cols[j]:
                    if st.session_state.revealed[i][j]:
                        # Show card content
                        st.button(
                            st.session_state.board[i][j],
                            key=f"button_{i}_{j}",
                            on_click=handle_click,
                            args=(i, j),
                        )
                    else:
                        # Show hidden card
                        st.button(
                            "❓",
                            key=f"button_{i}_{j}",
                            on_click=handle_click,
                            args=(i, j),
                        )

        # Check for game over
        if st.session_state.matches_found == 8:
            st.success(f"🎉 Congratulations! You won in {st.session_state.moves} moves!")
            if st.button("Play Again"):
                st.session_state.clear()
                st.rerun()

main()
