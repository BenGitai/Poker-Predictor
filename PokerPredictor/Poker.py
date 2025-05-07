import random
from itertools import combinations
import json
import os
import matplotlib.pyplot as plt


# Define card ranks and suits
RANKS = "23456789TJQKA"
SUITS = "♠♥♦♣"


def create_deck():
    """Creates a shuffled deck of 52 cards."""
    deck = [rank + suit for rank in RANKS for suit in SUITS]  # Generate all 52 possible cards
    random.shuffle(deck)  # Shuffle the deck randomly
    return deck

class PokerAI:
    def __init__(self, name, balance=1000, save_file="ai_data.json"):
        self.name = name
        self.balance = balance
        self.starting_balance = 0
        self.hand = []
        self.win_probability = 0
        self.history = []
        self.save_file = save_file

        # Behavior parameters (learning)
        self.bluff_chance = 0.1
        self.aggressive_threshold = 0.7
        self.cautious_threshold = 0.4

        self.q_table = {}  # Key: (rounded_probability, stage), Value: dict of action: Q-value
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.2  # Chance to try random move

        self.learning_log = []  # List of (round, balance, reward, exploration_rate)

        #self.load_ai_state()


    def update_win_probability(self, probability):
        """Update the AI's probability of winning."""
        self.win_probability = probability
        
    def save_ai_state(self):
        # Convert tuple keys in Q-table to strings
        q_table_serializable = {
            str(state): action_values for state, action_values in self.q_table.items()
        }


        ai_data = {
            "balance": self.balance,
            "history": self.history,
            "bluff_chance": self.bluff_chance,
            "aggressive_threshold": self.aggressive_threshold,
            "cautious_threshold": self.cautious_threshold,
            "q_table": q_table_serializable
        }

        with open(self.save_file, "w") as f:
            json.dump(ai_data, f)



    def load_ai_state(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    ai_data = json.load(f)
                    self.balance = ai_data.get("balance", 1000)
                    self.history = ai_data.get("history", [])
                    self.bluff_chance = ai_data.get("bluff_chance", 0.1)
                    self.aggressive_threshold = ai_data.get("aggressive_threshold", 0.7)
                    self.cautious_threshold = ai_data.get("cautious_threshold", 0.4)

                    # Convert string keys back to tuples
                    raw_q_table = ai_data.get("q_table", {})
                    self.q_table = {}
                    for key_str, actions in raw_q_table.items():
                        try:
                            state_tuple = eval(key_str)  # Turns "(1, 2)" → (1, 2)
                            self.q_table[state_tuple] = actions
                        except (SyntaxError, NameError):
                            continue  # skip corrupted entries


                    print(f"AI state loaded: Balance={self.balance}")
            except (json.JSONDecodeError, IOError, SyntaxError):
                print("Error loading AI state. Starting fresh.")
                self.__init__(self.name)
        else:
            print("No AI save file found. Starting fresh.")
            self.save_ai_state()


    def decide_bet(self, highest_bet, min_raise, total_pot, betting_stage):
        rounded_prob = round(self.win_probability, 1)
        state = (rounded_prob, betting_stage)

        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ["fold", "call", "raise", "bluff"]}

        # Epsilon-greedy choice
        if random.random() < self.exploration_rate:
            action = random.choice(list(self.q_table[state].keys()))
        else:
            action = max(self.q_table[state], key=self.q_table[state].get)

        self.last_state = state
        self.last_action = action
        
        if action == "raise" and self.win_probability < 0.6:
            action = "call" if highest_bet <= self.balance * 0.1 else "fold"

        # Translate action to bet
        if action == "fold":
            return 0
        elif action == "call":
            return highest_bet
        elif action == "raise":
            return min(self.balance, highest_bet + min_raise)
        elif action == "bluff":
            return min(self.balance, min_raise)

        return 0
    
    
    def update_q_value(self, reward):
        state = getattr(self, "last_state", None)
        action = getattr(self, "last_action", None)

        if state is None or action is None:
            print("No last state/action to update from.")
            return

        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ["fold", "call", "raise", "bluff"]}

        current_q = self.q_table[state].get(action, 0.0)
        max_future_q = max(self.q_table[state].values(), default=0.0)

        # Q-learning update
        new_q = ((1 - self.learning_rate) * current_q +
                self.learning_rate * (reward + self.discount_factor * max_future_q))

        self.q_table[state][action] = new_q

        print(f"Updated Q-value for {state} {action}: {current_q:.3f} → {new_q:.3f} (reward {reward})")

        # Decay exploration rate slightly
        self.exploration_rate = max(0.01, self.exploration_rate * 0.98)

        self.learning_log.append({
            "round": len(self.learning_log) + 1,
            "balance": self.balance,
            "reward": reward,
            "exploration": self.exploration_rate
        })

    
    def print_strategy_summary(self):
        print("\n--- AI Strategy Summary ---")
        for state in sorted(self.q_table):
            actions = self.q_table[state]
            best_action = max(actions, key=actions.get)
            print(f"State {state} → Best Action: {best_action} | Q-values: {actions}")

    def plot_learning_progress(self):
        if not self.learning_log:
            print("No data to plot.")
            return

        rounds = [entry["round"] for entry in self.learning_log]
        balances = [entry["balance"] for entry in self.learning_log]
        rewards = [entry["reward"] for entry in self.learning_log]
        exploration = [entry["exploration"] for entry in self.learning_log]

        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

        axs[0].plot(rounds, balances, label="AI Balance", color="blue")
        axs[0].set_ylabel("Balance")
        axs[0].legend()

        axs[1].plot(rounds, rewards, label="Reward", color="green")
        axs[1].set_ylabel("Reward")
        axs[1].legend()

        axs[2].plot(rounds, exploration, label="Exploration Rate", color="red")
        axs[2].set_ylabel("Exploration")
        axs[2].set_xlabel("Round")
        axs[2].legend()

        plt.tight_layout()
        plt.show()




#-----------------------------------------------------------------------------------------------------------------




class PokerGame:
    def __init__(self, num_players=2, first_better=1):
        """Initializes the game by creating a deck, players, and community cards."""
        self.deck = create_deck()  # Create and shuffle a new deck
        self.players = {f"Player {i+1}": [] for i in range(num_players)}
        self.ai_player = PokerAI("AI", save_file="ai_data.json")
        self.ai_player.load_ai_state()
        self.players["AI"] = self.ai_player  # Ensure AI is in the game

        self.ante_amount = 5
        self.community_cards = []  # List to hold the community cards (Flop, Turn, River)
        self.pot = 0  # Initialize the pot amount
        self.balances = {player: 1000 for player in self.players if player != "AI"}  # Each player starts with 1000 chips
        self.current_bets = {player: 0 for player in self.players}  # Track each player's bet in a round
        self.betting_stage = 0  # Tracks the current stage of betting (0: Pre-Flop, 1: Flop, 2: Turn, 3: River)
        self.first_better = first_better
        if self.first_better >= num_players:
            self.first_better = 0

    def deal_hole_cards(self):
        """Deals two hole cards to each player."""
        for player in self.players:
            self.players[player] = [self.deck.pop(), self.deck.pop()]
            if player == "AI":
                self.ai_player.hand = self.players[player]

            print(f"{player}'s Hole Cards: {self.players[player]}")  # Output the player's hole cards

    def deal_flop(self):
        """Deals three community cards (the Flop)."""
        self.community_cards.extend([self.deck.pop() for _ in range(3)])  # Draw three cards
        print(f"Flop: {self.community_cards}")
        self.betting_stage = 1
        self.betting_round()

    def deal_turn(self):
        """Deals   fourth community card (the Turn)."""
        self.community_cards.append(self.deck.pop())  # Draw one card
        print(f"Turn: {self.community_cards}")
        self.betting_stage = 2
        self.betting_round()

    def deal_river(self):
        """Deals the fifth community card (the River)."""
        self.community_cards.append(self.deck.pop())  # Draw one more card
        print(f"River: {self.community_cards}")
        self.betting_stage = 3
        self.betting_round()

    def get_best_hand(self, player):
        """Finds the best five-card hand for a player."""
        all_cards = self.players[player] + self.community_cards  # Combine hole cards and community cards
        return max(combinations(all_cards, 5), key=self.evaluate_hand)  # Choose the best 5-card combination

    def evaluate_hand(self, hand):
        """Evaluates the strength of a hand based on poker rules."""
        ranks = [card[0] for card in hand]  # Extract the rank of each card
        suits = [card[1] for card in hand]  # Extract the suit of each card

        # Count occurrences of each rank
        rank_counts = {rank: ranks.count(rank) for rank in RANKS}
        max_same_rank = max(rank_counts.values())  # Get max frequency of any rank
        
        # Check for flush (all suits the same)
        is_flush = len(set(suits)) == 1
        
        # Check for straight (5 consecutive ranks)
        sorted_ranks = sorted([RANKS.index(rank) for rank in ranks])
        is_straight = all(sorted_ranks[i] + 1 == sorted_ranks[i + 1] for i in range(len(sorted_ranks) - 1))
        
        # Assign a basic strength score (higher is better)
        if is_flush and is_straight:
            return 8  # Straight Flush
        elif max_same_rank == 4:
            return 7  # Four of a Kind
        elif max_same_rank == 3 and 2 in rank_counts.values():
            return 6  # Full House
        elif is_flush:
            return 5  # Flush
        elif is_straight:
            return 4  # Straight
        elif max_same_rank == 3:
            return 3  # Three of a Kind
        elif list(rank_counts.values()).count(2) == 2:
            return 2  # Two Pair
        elif max_same_rank == 2:
            return 1  # One Pair
        else:
            return 0  # High Card
    
    def showdown(self):
        """Determines the winner by comparing hand rankings."""
        if len(self.players) == 1:
            winner = list(self.players.keys())[0]
        else:
            best_hands = {player: self.get_best_hand(player) for player in self.players}
            best_scores = {player: self.evaluate_hand(hand) for player, hand in best_hands.items()}
            winner = max(best_scores, key=best_scores.get)
        
        print(f"Winner: {winner}, Pot: {self.pot}")
        if winner == "AI":
            self.ai_player.balance += self.pot
        else:
            self.balances[winner] += self.pot

        self.ai_player.save_ai_state()

        ending_balance = self.ai_player.balance
        starting_balance = self.ai_player.starting_balance  # Profit/loss
        if winner == "AI":
            reward = ending_balance - starting_balance
        elif "AI" in self.players:
            reward = ending_balance - starting_balance  # Lost at showdown
        else:
            reward = 0  # Folded

        reward = reward / 100  # Normalize to manageable range
        print(f"Reward: {reward}, Start: {self.ai_player.starting_balance}, End: {self.ai_player.balance}")
        self.ai_player.update_q_value(reward)
        
    
    def betting_round(self):
        """Handles a structured betting round where players must call after a raise."""
        active_players = list(self.players.keys())
        for i in range (self.first_better):
            active_players.append(active_players.pop(0))
        #random.shuffle(active_players)  # Randomize betting order
        highest_bet = 0
        betting_continues = True

        while betting_continues:
            betting_continues = False  # Reset flag; if no one raises, betting will end
            players_to_bet = active_players[:]  # Keep track of players needing to act
            betting_continues = False
            for player in players_to_bet[:]:  # Iterate over tracked players  # Iterate over a copy in case of removal
                if player not in self.players:
                    continue
                
                hand_strength = self.evaluate_hand(self.get_best_hand(player))
                win_probability = (hand_strength + 1) / 9  # Normalize probability
                if player == "AI":
                    self.ai_player.update_win_probability(win_probability)

                variability = random.uniform(1.0, 1.0)  # Increase lower bound to encourage calling
                if player == "AI":
                    bet_amount = self.ai_player.decide_bet(highest_bet, 10, self.pot, self.betting_stage)
                    bet_amount = min(bet_amount, self.ai_player.balance)
                else:
                    bet_amount = int(win_probability * self.balances[player] * 0.1 * variability)
                    bet_amount = min(bet_amount, self.balances[player])
                
                if highest_bet == 0:
                    highest_bet = bet_amount
                    self.current_bets[player] = bet_amount
                    if player == "AI":
                        self.ai_player.balance -= bet_amount
                    else:
                        self.balances[player] -= bet_amount

                    self.pot += bet_amount
                    if player == "AI":
                        print(f"{player} bets {bet_amount}. Remaining balance: {self.ai_player.balance}")
                    else:
                        print(f"{player} bets {bet_amount}. Remaining balance: {self.balances[player]}")
                else:
                    if bet_amount > highest_bet * 1 and player in self.players and player not in self.current_bets:
                        raise_amount = min(self.balances[player], bet_amount)
                        highest_bet = raise_amount
                        self.current_bets[player] = raise_amount
                        if player == "AI":
                            self.ai_player.balance -= raise_amount
                        else:
                            self.balances[player] -= raise_amount

                        self.pot += raise_amount
                        print(f"{player} raises to {raise_amount}. Remaining balance: {self.balances[player]}")
                        betting_continues = True  # Ensure previous callers bet again
                    elif bet_amount >= highest_bet * 0.75 or random.random() < 0.15:  # Lowered threshold + 15% bluff chance
                        self.current_bets[player] = highest_bet
                        if player == "AI":
                            self.ai_player.balance -= highest_bet
                        else:
                            self.balances[player] -= highest_bet
                        self.pot += highest_bet
                        if player == "AI":
                            print(f"{player} calls {highest_bet}. Remaining balance: {self.ai_player.balance}")
                        else:
                            print(f"{player} calls {highest_bet}. Remaining balance: {self.balances[player]}")
                    else:
                        print(f"{player} folds.")
                        active_players.remove(player)
                        del self.players[player]
    
    def play_round(self):
        """Runs a full round of poker by dealing cards, betting, and determining the winner."""
        self.ai_player.starting_balance = self.ai_player.balance
        # Deduct ante from all players
        for player in list(self.players.keys()):
            if player == "AI":
                if self.ai_player.balance >= self.ante_amount:
                    self.ai_player.balance -= self.ante_amount
                    self.pot += self.ante_amount
                else:
                    print(f"{player} cannot afford ante and is eliminated.")
                    del self.players[player]
            else:
                if self.balances[player] >= self.ante_amount:
                    self.balances[player] -= self.ante_amount
                    self.pot += self.ante_amount
                else:
                    print(f"{player} cannot afford ante and is eliminated.")
                    del self.players[player]

        self.deal_hole_cards()
        self.deal_flop()
        self.deal_turn()
        self.deal_river()
        return self.showdown()
    
    def reset_game(self):
        """Resets the game state for a new round."""
        self.deck = create_deck()
        self.players = {player: [] for player in self.balances if self.balances.get(player, 0) > 0}
        if self.ai_player.balance > 0:
            self.players["AI"] = self.ai_player
        self.current_bets = {player: 0 for player in self.players}
        self.community_cards = []
        self.pot = 0
        self.current_bets = {player: 0 for player in self.players}
        self.betting_stage = 0

#-------------------------------------------------------------------------------------------------------------------------

# Run a test game with multiple players
game = PokerGame(num_players=5, first_better=1)

#while True:
i = 0
while game.ai_player.balance > 0 and i < 1000:
        i+=1
        result = game.play_round()
        print(result)  # Output the result of the game
        game.ai_player.print_strategy_summary()
        for player in game.balances:
            print(game.balances[player])
        print(f"AI balance: {game.ai_player.balance}")
        #input("Press Enter to continue...")
        game.first_better = game.first_better + 1

        """
        if len(game.ai_player.learning_log) % 10 == 0:  # Plot every 10 rounds
            game.ai_player.plot_learning_progress()
        """
        game.reset_game()
print(f"Rounds: {i}")
game.ai_player.plot_learning_progress()