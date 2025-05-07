import random
from itertools import combinations
import json
import os
import matplotlib.pyplot as plt
import sys
import copy
import time
import plotly.graph_objs as go
from plotly.subplots import make_subplots



# Define card ranks and suits
RANKS = "23456789TJQKA"
SUITS = "♠♥♦♣"


def create_deck():
    """Creates a shuffled deck of 52 cards."""
    deck = [rank + suit for rank in RANKS for suit in SUITS]  # Generate all 52 possible cards
    random.shuffle(deck)  # Shuffle the deck randomly
    return deck

def print_progress_bar(current, total, bar_length=40, elapsed=None, eta=None):
    percent = current / total
    arrow = "=" * int(percent * bar_length - 1) + ">" if percent < 1 else "=" * bar_length
    spaces = " " * (bar_length - len(arrow))
    
    time_info = ""
    if elapsed is not None and eta is not None:
        time_info = f" | Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s"
    
    sys.stdout.write(f"\r[{arrow}{spaces}] {int(percent * 100)}% ({current}/{total}){time_info}")
    sys.stdout.flush()

    if current == total:
        print()  # Move to new line at end



#-----------------------------------------------------------------------------------------------------------------


class PokerAI:
    def __init__(self, name, balance=1000, save_file="ai_data.json", load=True):
        self.name = name
        self.balance = balance
        self.starting_balance = 0
        self.hand = []
        self.win_probability = 0
        self.history = []
        self.save_file = save_file

        self.all_in = False

        # Behavior parameters (learning)
        self.bluff_chance = 0.1
        self.aggressive_threshold = 0.7
        self.cautious_threshold = 0.4

        self.raise_threshold = 0.7
        self.call_threshold = 0.4


        self.q_table = {}  # Key: (rounded_probability, stage), Value: dict of action: Q-value
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.2  # Chance to try random move

        self.learning_log = []  # List of (round, balance, reward, exploration_rate)

        self.stagnation_counter = 0
        self.prev_balance = balance
        self.prev_q_table_size = 0

        self.total_resets = 0

        self.reset_rounds = []
        if load:
            self.load_ai_state()


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
            "raise_threshold": self.raise_threshold,
            "call_threshold": self.call_threshold,
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
                    self.raise_threshold = ai_data.get("raise_threshold", 0.7)
                    self.call_threshold = ai_data.get("call_threshold", 0.4)


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
        agg = round(self.estimate_opponent_aggression(), 1)
        state = (
            rounded_prob,
            betting_stage,
            agg
        )


        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ["fold", "call", "raise", "bluff"]}

        # Epsilon-greedy choice
        if random.random() < self.exploration_rate:
            action = random.choice(list(self.q_table[state].keys()))
        else:
            action = max(self.q_table[state], key=self.q_table[state].get)

        self.last_state = state
        self.last_action = action
        
        if len(self.learning_log) > 10 and len(self.learning_log) % 20 == 0:
            recent = self.learning_log[-10:]
            valid_rewards = [e['reward'] for e in recent if e['reward'] is not None]
            if valid_rewards:
                avg_reward = sum(valid_rewards) / len(valid_rewards)
            else:
                avg_reward = 0  # or some neutral default

            last_reset = self.reset_rounds[-1] if self.reset_rounds else 0
            recent = self.learning_log[last_reset:]

            if avg_reward < 0.1 and last_reset > 5:  # underperforming
                #print(f"{self.name} mutating thresholds...")
                self.bluff_chance = max(0, min(1, self.bluff_chance + random.uniform(-0.02, 0.02)))
                self.raise_threshold = max(0, min(1, self.raise_threshold + random.uniform(-0.05, 0.05)))
                self.call_threshold = max(0, min(1, self.call_threshold + random.uniform(-0.05, 0.05)))


        if action == "raise" and self.win_probability < 0.6:
            action = "call" if highest_bet <= self.balance * 0.1 else "fold"

        if action == "fold" and self.win_probability > 0.4:
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
            #print("No last state/action to update from.")
            return

        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ["fold", "call", "raise", "bluff"]}

        current_q = self.q_table[state].get(action, 0.0)
        max_future_q = max(self.q_table[state].values(), default=0.0)

        # Q-learning update
        new_q = ((1 - self.learning_rate) * current_q +
                self.learning_rate * (reward + self.discount_factor * max_future_q))

        self.q_table[state][action] = new_q

        #print(f"Updated Q-value for {state} {action}: {current_q:.3f} → {new_q:.3f} (reward {reward})")

        # Decay exploration rate slightly
        self.exploration_rate = max(0.01, self.exploration_rate * 0.98)

        # Discourage excessive all-ins
        recent = self.learning_log[-5:]
        if sum(1 for r in recent if r.get("balance") == 0) >= 3:
            reward -= 5


        q_table_growth = len(self.q_table) - self.prev_q_table_size
        balance_change = abs(self.balance - self.prev_balance)

        if balance_change < 1 and q_table_growth == 0:
            self.stagnation_counter += 1
        else:
            self.stagnation_counter = 0  # Reset if anything meaningful changed

        self.prev_balance = self.balance
        self.prev_q_table_size = len(self.q_table)

        if self.stagnation_counter >= 20:
            #print(f"{self.name} is stagnant — applying small mutation")
            self.bluff_chance = max(0, min(1, self.bluff_chance + random.uniform(-0.02, 0.02)))
            self.call_threshold = max(0, min(1, self.call_threshold + random.uniform(-0.05, 0.05)))
            self.raise_threshold = max(0, min(1, self.raise_threshold + random.uniform(-0.05, 0.05)))
            self.exploration_rate = min(0.5, self.exploration_rate + 0.05)

            self.stagnation_counter = 0  # Reset
            self.balance = 1000
            self.reset_rounds.append(len(self.learning_log))


        self.learning_log.append({
            "round": len(self.learning_log) + 1,
            "balance": self.balance,
            "reward": reward,
            "exploration": self.exploration_rate,
            "mutated": self.stagnation_counter == 0
        })
    
    def estimate_opponent_aggression(self):
        """Estimate how aggressive opponents are based on last N rounds."""
        if not self.history:
            return 0.5  # Neutral aggression

        # Count recent actions
        recent = self.history[-10:]
        raise_count = sum(1 for act in recent if act == "raise")
        call_count = sum(1 for act in recent if act == "call")
        fold_count = sum(1 for act in recent if act == "fold")

        total = max(1, raise_count + call_count + fold_count)
        return raise_count / total  # Simple aggression proxy


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

        fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        # Balance and exploration
        axs[0].plot(rounds, balances, label="Balance", color="blue")
        axs[0].set_ylabel("Balance")
        axs[0].legend(loc="upper left")

        axs[0].twinx().plot(rounds, exploration, label="Exploration", color="red", linestyle="dashed")
        axs[0].set_ylabel("Exploration Rate", color="red")
        axs[0].tick_params(axis='y', labelcolor='red')

        # Reward history
        axs[1].plot(rounds, rewards, label="Reward", color="green")
        axs[1].set_ylabel("Reward")
        axs[1].set_xlabel("Round")
        axs[1].legend()

        plt.tight_layout()
        plt.show()

        for r in self.reset_rounds:
            axs[0].axvline(x=r, color='gray', linestyle='--', alpha=0.5)
            axs[1].axvline(x=r, color='gray', linestyle='--', alpha=0.5)



    def mutate_from(self, parent_ai):
        import copy
        self.q_table = copy.deepcopy(parent_ai.q_table)
        self.bluff_chance = parent_ai.bluff_chance + random.uniform(-0.02, 0.02)
        self.call_threshold = parent_ai.call_threshold + random.uniform(-0.05, 0.05)
        self.raise_threshold = parent_ai.raise_threshold + random.uniform(-0.05, 0.05)
        self.exploration_rate = 0.2

    def estimate_opponent_aggression(self):
        """Estimate how aggressive opponents are based on past actions."""
        if not self.history:
            return 0.5  # Neutral default

        recent = self.history[-10:]
        raise_count = sum(1 for act in recent if act == "raise")
        call_count = sum(1 for act in recent if act == "call")
        fold_count = sum(1 for act in recent if act == "fold")
        total = max(1, raise_count + call_count + fold_count)

        return raise_count / total


#-----------------------------------------------------------------------------------------------------------------

class BotPlayer:
    def __init__(self, name, balance=1000):
        self.name = name
        self.balance = balance
        self.hand = []
        self.win_probability = 0
        self.starting_balance = 0  # for reward tracking

        # Tunable behavior params
        self.call_threshold = 0.25
        self.raise_threshold = 0.6
        self.bluff_chance = 0.1  # increase slightly

        self.all_in = False


    def update_win_probability(self, probability):
        self.win_probability = probability

    def decide_bet(self, highest_bet, min_raise, total_pot, betting_stage):
        buffer = random.uniform(-0.05, 0.1)  # variability & bluff potential
        adjusted_prob = self.win_probability + buffer

        # Dynamic willingness based on balance and pot
        willingness = self.balance * adjusted_prob

        # Bluff logic
        if random.random() < self.bluff_chance:
            bluff_bet = min(self.balance, max(min_raise, int(self.balance * 0.05)))
            #print(f"{self.name} is bluffing with {bluff_bet}")
            return bluff_bet

        # Strong hand → raise
        if adjusted_prob >= self.raise_threshold:
            raise_amount = highest_bet + int(total_pot * 0.1)
            return min(self.balance, raise_amount)

        # Decent hand → call if it's not too costly
        if adjusted_prob >= self.call_threshold:
            if highest_bet <= willingness:
                return min(self.balance, highest_bet)

        # Otherwise → fold
        return 0



#-----------------------------------------------------------------------------------------------------------------


class PokerGame:
    def __init__(self, num_ai=2, num_bots=1, ante_amount=5):
        self.deck = []
        self.players = {}  # name -> PokerAI instance
        self.community_cards = []
        self.pot = 0
        self.ante_amount = ante_amount
        self.betting_stage = 0  # 0 = pre-flop, 1 = flop, 2 = turn, 3 = river
        self.first_better = 0
        self.all_players = {}

        self.num_ai = num_ai
        self.num_bots = num_bots


        # Add AIs
        for i in range(num_ai):
            name = f"AI_{i+1}"
            ai = PokerAI(name, save_file=f"{name}.json")
            self.players[name] = ai
            self.all_players[name] = ai

        for i in range(num_bots):
            name = f"BOT_{i+1}"
            bot = BotPlayer(name)
            self.players[name] = bot
            self.all_players[name] = bot

    def is_ai(self, player_name):
        return isinstance(self.all_players.get(player_name), PokerAI)

    def is_bot(self, player_name):
        return isinstance(self.all_players.get(player_name), BotPlayer)

    def reset_game(self):
        """Resets game state for a new hand."""
        self.deck = create_deck()
        self.community_cards = []
        self.pot = 0
        self.betting_stage = 0
        self.folded_players = set()

        # Re-add all players with chips remaining
        self.players = {
            name: p for name, p in self.all_players.items() if p.balance > 0
        }
        self.first_better = (self.first_better + 1) % len(self.players)


    def deal_hole_cards(self):
        for player in self.players.values():
            player.hand = [self.deck.pop(), self.deck.pop()]

    def deal_flop(self):
        self.community_cards += [self.deck.pop() for _ in range(3)]
        #print(f"Flop: {self.community_cards}")

    def deal_turn(self):
        self.community_cards.append(self.deck.pop())
        #print(f"Turn: {self.community_cards[-1]}")

    def deal_river(self):
        self.community_cards.append(self.deck.pop())
        #print(f"River: {self.community_cards[-1]}")

    def betting_round(self, stage):
        #print(f"\n--- Betting Round {stage} ---")
        self.betting_stage = stage
        active_players = list(self.players.keys())
        current_bets = {name: 0 for name in active_players}
        highest_bet = 0
        folded_players = set()

        # Rotate players so first better changes each round
        rotated_players = active_players[self.first_better:] + active_players[:self.first_better]


        first_to_act = rotated_players[0]
        player = self.players[first_to_act]
        forced_bet = min(10, player.balance)
        player.balance -= forced_bet
        self.pot += forced_bet
        current_bets[first_to_act] = forced_bet
        highest_bet = forced_bet

        #print(f"{first_to_act} starts betting with {forced_bet}")


        betting_complete = False
        while not betting_complete:
            betting_complete = True  # assume complete unless someone raises

            for player_name in rotated_players:
                if player_name in folded_players:
                    continue

                player = self.players[player_name]

                num_opponents = len(self.players) - 1
                win_prob = self.estimate_win_probability(player, simulations=50, num_opponents=num_opponents)
                player.update_win_probability(win_prob)


                current_bet = current_bets[player_name]
                call_amount = highest_bet - current_bet

                bet = player.decide_bet(
                    highest_bet=highest_bet,
                    min_raise=0,
                    total_pot=self.pot,
                    betting_stage=stage
                )
                bet = min(bet, player.balance)

                if bet == player.balance:
                    #print(f"{player_name} goes all in")
                    player.all_in = True
                else:
                    player.all_in = False



                if bet < call_amount:
                    #print(f"{player_name} folds.")
                    folded_players.add(player_name)
                    #del self.players[player_name]
                    if self.is_ai(player_name):
                        player.history.append("fold")
                        player.history = player.history[-50:]

                    continue

                player.balance -= bet
                total_bet = current_bets[player_name] + bet
                current_bets[player_name] = total_bet
                self.pot += bet

                if total_bet > highest_bet:
                    highest_bet = total_bet
                    betting_complete = False  # someone raised, continue loop
                    if self.is_ai(player_name):
                        if bet == highest_bet and call_amount > 0:
                            action = "call"
                        elif bet > call_amount:
                            action = "raise"
                        else:
                            action = "bluff" if bet < call_amount else "check"

                        player.history.append(action)
                        player.history = player.history[-50:]


                #print(f"{player_name} bets {bet} (Total: {total_bet}, Balance: {player.balance})")

            # Remove folded players from rotation
            rotated_players = [p for p in rotated_players if p not in folded_players]

            if len(rotated_players) <= 1:
                break  # everyone else folded
        # At the end of the round

        # Update who's first next round
        self.first_better = (self.first_better + 1) % len(self.players)
        self.players = {p: self.players[p] for p in self.players if p not in folded_players}

    def estimate_win_probability(self, player, simulations=100, num_opponents=1):
        from random import sample
        from itertools import combinations

        deck = create_deck()
        known_cards = player.hand + self.community_cards

        # Remove known cards from the deck
        for card in known_cards:
            if card in deck:
                deck.remove(card)

        wins = 0
        ties = 0

        for _ in range(simulations):
            # Clone the deck and shuffle
            sim_deck = deck[:]

            # Generate missing community cards
            remaining_community = 5 - len(self.community_cards)
            sim_community = self.community_cards + [sim_deck.pop() for _ in range(remaining_community)]

            # Get player's full hand
            player_best = max(combinations(player.hand + sim_community, 5), key=self.evaluate_hand)
            player_score = self.evaluate_hand(player_best)

            # Generate opponents and compare
            player_won = True
            tie = False

            for _ in range(num_opponents):
                opp_hand = [sim_deck.pop(), sim_deck.pop()]
                opp_best = max(combinations(opp_hand + sim_community, 5), key=self.evaluate_hand)
                opp_score = self.evaluate_hand(opp_best)

                if opp_score > player_score:
                    player_won = False
                    break
                elif opp_score == player_score:
                    tie = True

            if player_won and not tie:
                wins += 1
            elif tie:
                ties += 1

        return (wins + 0.5 * ties) / simulations


    def evaluate_hand(self, cards):
        """Returns a numerical score for a 5-card hand."""
        ranks = "23456789TJQKA"
        rank_values = {r: i for i, r in enumerate(ranks, 2)}
        
        # Get rank counts and suit counts
        values = sorted([rank_values[c[0]] for c in cards], reverse=True)
        suits = [c[1] for c in cards]
        unique_vals = sorted(set(values), reverse=True)
        val_counts = {v: values.count(v) for v in unique_vals}

        is_flush = len(set(suits)) == 1
        is_straight = len(unique_vals) == 5 and (unique_vals[0] - unique_vals[-1] == 4)

        # Special case: A-2-3-4-5 straight
        if set(values) == {14, 5, 4, 3, 2}:
            is_straight = True
            unique_vals = [5, 4, 3, 2, 1]

        if is_flush and is_straight and max(unique_vals) == 14:
            return (9, unique_vals)  # Royal Flush
        elif is_flush and is_straight:
            return (8, unique_vals)  # Straight Flush
        elif 4 in val_counts.values():
            four = [v for v in val_counts if val_counts[v] == 4][0]
            kicker = max([v for v in unique_vals if v != four])
            return (7, [four]*4 + [kicker])
        elif sorted(val_counts.values()) == [2, 3]:
            three = [v for v in val_counts if val_counts[v] == 3][0]
            pair = [v for v in val_counts if val_counts[v] == 2][0]
            return (6, [three]*3 + [pair]*2)
        elif is_flush:
            return (5, values)
        elif is_straight:
            return (4, unique_vals)
        elif 3 in val_counts.values():
            three = [v for v in val_counts if val_counts[v] == 3][0]
            kickers = [v for v in unique_vals if v != three]
            return (3, [three]*3 + kickers)
        elif list(val_counts.values()).count(2) == 2:
            pairs = sorted([v for v in val_counts if val_counts[v] == 2], reverse=True)
            kicker = [v for v in unique_vals if v not in pairs][0]
            return (2, pairs*2 + [kicker])
        elif 2 in val_counts.values():
            pair = [v for v in val_counts if val_counts[v] == 2][0]
            kickers = [v for v in unique_vals if v != pair]
            return (1, [pair]*2 + kickers)
        else:
            return (0, values)  # High card
        

    def showdown(self):
        if len(self.players) == 1:
            winner = list(self.players.keys())[0]
        else:
            best_scores = {}
            for name, player in self.players.items():
                if hasattr(self, 'folded_players') and name in self.folded_players:
                    continue  # Skip folded players

                all_cards = player.hand + self.community_cards
                best_five = max(combinations(all_cards, 5), key=self.evaluate_hand)
                best_scores[name] = self.evaluate_hand(best_five)

            if not best_scores:
                #print("No players to show down — all folded?")
                return

            winner = max(best_scores, key=best_scores.get)

        #print(f"\nWinner: {winner} wins the pot of {self.pot} chips!")
        self.players[winner].balance += self.pot

        for name, player in self.all_players.items():
            if not self.is_ai(name):
                continue

            # Reward is based on how well they did, not just survival
            reward = (player.balance - player.starting_balance) / 20

            # Add a survival reward if they played at all
            participated = any(action != "fold" for action in player.history[-5:])
            if participated:
                reward += 1  # small survival bonus

            # Penalize passivity
            fold_ratio = sum(1 for a in player.history[-5:] if a == "fold") / 5
            if fold_ratio >= 0.8:
                reward -= 2  # discouraged overly passive play

            if player.all_in:
                #print(f"{name} punished for going all in")
                reward = -15  # discourage reckless all-ins
                #print(reward)

            player.update_q_value(reward)
            player.save_ai_state()



    def play_round(self):
        #print("\n--- New Round ---")

        # Deduct ante and eliminate broke players
        eliminated = []
        for name, player in self.players.items():
            if player.balance < self.ante_amount:
                #print(f"{name} eliminated (balance too low).")
                eliminated.append(name)
            else:
                player.balance -= self.ante_amount
                self.pot += self.ante_amount
                player.starting_balance = player.balance

        #for name in eliminated:
            #del self.players[name]

        if len(self.players) <= 1:
            #print("Not enough players to continue.")
            return

        self.deal_hole_cards()
        #for name, player in self.players.items():
            #print(f"{name}'s hand: {player.hand}")

        self.betting_round(stage=0)

        self.deal_flop()
        self.betting_round(stage=1)

        self.deal_turn()
        self.betting_round(stage=2)

        self.deal_river()
        self.betting_round(stage=3)

        self.showdown()


    def reset_all_ais_from_winner(self, winner_ai):
        import copy

        for i in range(self.num_ai):
            name = f"AI_{i+1}"

            # Preserve existing AI if possible
            if name in self.all_players:
                ai = self.all_players[name]
            else:
                ai = PokerAI(name=name, save_file=f"{name}.json", load=False)
                ai.learning_log = []
                ai.reset_rounds = []
                ai.total_resets = 0

            # Mutate strategy from winner
            ai.q_table = copy.deepcopy(winner_ai.q_table)
            ai.bluff_chance = min(max(winner_ai.bluff_chance + random.uniform(-0.02, 0.02), 0), 1)
            ai.call_threshold = min(max(winner_ai.call_threshold + random.uniform(-0.05, 0.05), 0), 1)
            ai.raise_threshold = min(max(winner_ai.raise_threshold + random.uniform(-0.05, 0.05), 0), 1)

            # Reset gameplay stats
            ai.balance = 1000
            ai.starting_balance = 1000
            ai.exploration_rate = 0.2
            ai.stagnation_counter = 0
            ai.all_in = False
            ai.total_resets = getattr(ai, "total_resets", 0) + 1

            # Track generation reset in learning log
            ai.reset_rounds.append(len(ai.learning_log))
            # Insert None to create a gap in plotting
            ai.learning_log.append({
                "round": len(ai.learning_log) + 1,
                "balance": 1000,
                "reward": 0,
                "exploration": 0.2
            })


            # Save and register
            ai.save_ai_state()
            self.players[name] = ai
            self.all_players[name] = ai

        # Recreate bots
        for i in range(self.num_bots):
            name = f"BOT_{i+1}"
            bot = BotPlayer(name)
            bot.balance = 1000
            self.players[name] = bot
            self.all_players[name] = bot

        # Reset game state
        self.deck = create_deck()
        self.community_cards = []
        self.pot = 0
        self.folded_players = set()
        self.first_better = 0
        self.reset_game()

    def reset_all_ais_from_parents(self, parent1, parent2):
        import copy

        combined_q = combine_q_tables(parent1.q_table, parent2.q_table)

        for i in range(self.num_ai):
            name = f"AI_{i+1}"

            if name in self.all_players:
                ai = self.all_players[name]
            else:
                ai = PokerAI(name=name, save_file=f"{name}.json", load=False)
                ai.learning_log = []
                ai.reset_rounds = []
                ai.total_resets = 0

            ai.q_table = copy.deepcopy(combined_q)

            # Combine traits
            def blend(a, b, spread=0.05):
                return min(max((a + b) / 2 + random.uniform(-spread, spread), 0), 1)

            ai.bluff_chance = blend(parent1.bluff_chance, parent2.bluff_chance, 0.02)
            ai.call_threshold = blend(parent1.call_threshold, parent2.call_threshold)
            ai.raise_threshold = blend(parent1.raise_threshold, parent2.raise_threshold)

            # Reset for new gen
            ai.balance = 1000
            ai.starting_balance = 1000
            ai.learning_log.append({
                "round": len(ai.learning_log) + 1,
                "balance": 1000,
                "reward": 0,
                "exploration": 0.2
            })

            ai.exploration_rate = 0.2
            ai.stagnation_counter = 0
            ai.all_in = False
            ai.total_resets = getattr(ai, "total_resets", 0) + 1
            ai.reset_rounds.append(len(ai.learning_log))
            ai.save_ai_state()

            self.players[name] = ai
            self.all_players[name] = ai

        # Rebuild bots (unchanged)
        for i in range(self.num_bots):
            name = f"BOT_{i+1}"
            bot = BotPlayer(name)
            bot.balance = 1000
            self.players[name] = bot
            self.all_players[name] = bot

        self.deck = create_deck()
        self.community_cards = []
        self.pot = 0
        self.folded_players = set()
        self.first_better = 0





#-----------------------------------------------------------------------------------------------------------------

def plot_all_ai_learning_progress(ai_players):
    if not ai_players:
        print("No AI players to plot.")
        return

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("AI Balance", "AI Reward"))

    for ai in ai_players:
        rounds = [entry["round"] for entry in ai.learning_log if entry.get("balance") is not None]
        balances = [entry["balance"] for entry in ai.learning_log if entry.get("balance") is not None]
        rewards = [entry["reward"] for entry in ai.learning_log if entry.get("reward") is not None]

        fig.add_trace(go.Scatter(x=rounds, y=balances, mode='lines', name=f'{ai.name} Balance'),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=rounds, y=rewards, mode='lines', name=f'{ai.name} Reward'),
                      row=2, col=1)

        # Reset markers
        for r in ai.reset_rounds:
            fig.add_vline(x=r, line_width=1, line_dash="dash", line_color="gray", row=1, col=1)
            fig.add_vline(x=r, line_width=1, line_dash="dash", line_color="gray", row=2, col=1)

    fig.update_layout(
        height=600,
        title="AI Learning Progress",
        xaxis=dict(
            rangeslider=dict(visible=True),  # This adds the scrollable slider
            type="linear"
        ),
        xaxis2=dict(
            rangeslider=dict(visible=False),
            type="linear"
        ),
        showlegend=True
    )

    fig.show()




#-----------------------------------------------------------------------------------------------------------------


def combine_q_tables(q1, q2):
    combined = {}
    for state in set(q1.keys()) | set(q2.keys()):
        a1 = q1.get(state, {})
        a2 = q2.get(state, {})
        combined[state] = {}

        actions = set(a1.keys()) | set(a2.keys())
        for action in actions:
            qval1 = a1.get(action, 0)
            qval2 = a2.get(action, 0)
            combined[state][action] = (qval1 + qval2) / 2
    return combined

#-----------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    game = PokerGame(num_ai=5, num_bots=1)

    total_rounds = 1000
    generation = 0
    start_time = time.time()
    
    for i in range(total_rounds):
        #print(f"\n=== Round {i+1} ===")
        game.reset_game()
        #print("\nAIs after reset:")
        #for name, player in game.players.items():
            #print(f"{name}: balance={player.balance}")
        elapsed_time = time.time() - start_time
        avg_time_per_round = elapsed_time / (i + 1)
        game_eta = avg_time_per_round * (total_rounds - (i + 1))

        print_progress_bar(i, total_rounds, elapsed=elapsed_time, eta=game_eta)
        
        # Only count AIs that are still in all_players and have chips
        active_ais = [
            name for name, player in game.all_players.items()
            if game.is_ai(name) and player.balance > game.ante_amount
        ]

        if len(active_ais) == 2:
            # This is now a legit generation end
            parent1 = active_ais[0]
            parent2 = active_ais[1]

            # Trigger generation reset here

            parent1_name = active_ais[0]
            parent2_name = active_ais[0]
            parent1 = game.players[parent1_name]
            parent2 = game.players[parent2_name]
            #print(f"\n{parent1_name} is parent 1")
            #print(f"\n{parent2_name} is parent 2")

            # Save the winner's state
            parent1.save_ai_state()
            parent2.save_ai_state()

            # Evolve a new generation from the winner
            game.reset_all_ais_from_parents(parent1, parent2)
            #print("\nNew Generation AIs and Bots (Parents):")
            #for name in game.players:
                #print(f"{name}: {game.players[name].balance}")


            generation += 1
            #print(f"\nStarting Generation {generation}...")
            #continue

            #continue

        elif len(active_ais) == 1:
            # This is now a legit generation end
            winner = active_ais[0]

            # Trigger generation reset here

            winner_name = active_ais[0]
            winner = game.players[winner_name]
            #print(f"\n{winner_name} is the last AI standing!")

            # Save the winner's state
            winner.save_ai_state()

            # Evolve a new generation from the winner
            game.reset_all_ais_from_winner(winner)
            #print("\nNew Generation AIs and Bots (Winner):")
            #for name in game.players:
                #print(f"{name}: {game.players[name].balance}")


            generation += 1
            #print(f"\nStarting Generation {generation}...")
            #continue
    
        game.folded_players = set()

        game.play_round()
        

    game.reset_game()
    ai_players = []

    for name, player in game.players.items():
        if game.is_ai(name):
            ai_players.append(player)

            print(f"\nSummary for {name}")
            print("-" * 30)
            print(f"Final Balance: {player.balance}")
            print(f"Q-table size: {len(player.q_table)}")
            #print(f"Resets: {getattr(player, 'total_resets', 0)}")
    ai_players = [p for p in game.all_players.values() if isinstance(p, PokerAI)]
    plot_all_ai_learning_progress(ai_players)