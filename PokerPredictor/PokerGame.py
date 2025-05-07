import json
from Poker2 import PokerAI

def parse_cards(card_str):
    return card_str.strip().upper().split()

def get_opponent_actions(start, end, num_players):
    actions = []
    for i in range(start, end):
        player_index = (i % num_players) + 1
        action = input(f"Player {player_index}'s action (fold/call/raise amount): ").strip().lower()
        actions.append((f"Player_{player_index}", action))
    return actions

def main():
    ai = PokerAI(name="Trained_AI", save_file="AI_1.json")
    ai.load_ai_state()

    num_players = int(input("Enter total number of players at the table: "))
    ai.balance = int(input("Enter AI's starting chip balance: "))

    while True:
        pot = 0
        highest_bet = 0
        current_bets = {f"Player_{i+1}": 0 for i in range(num_players)}
        folded = set()

        ai.hand = parse_cards(input("Enter AI's hole cards (e.g., 'AH KS'): "))
        ai_position = int(input(f"Enter AI's position (1 to {num_players}): ")) - 1

        community_cards = []
        stage = 0

        while stage < 4:
            print(f"\n--- Betting Round {stage} ---")
            actions_before_ai = get_opponent_actions(ai_position + 1, ai_position + num_players, num_players)

            for player, action in actions_before_ai:
                if action.startswith("fold"):
                    folded.add(player)
                elif action.startswith("call"):
                    pot += highest_bet - current_bets[player]
                    current_bets[player] = highest_bet
                elif action.startswith("raise"):
                    try:
                        amount = int(action.split()[1])
                    except:
                        print("Invalid raise amount. Skipping.")
                        continue
                    highest_bet = amount
                    current_bets[player] = amount
                    pot += amount
                ai.history.append(action.split()[0])

            ai.update_win_probability(0.5)  # Placeholder
            bet = ai.decide_bet(highest_bet, min_raise=0, total_pot=pot, betting_stage=stage)

            if bet == 0:
                print("AI folds.")
                break  # AI folded, end hand

            print(f"AI bets {bet}")
            ai.balance -= bet
            pot += bet
            current_bets["AI"] = bet

            actions_after_ai = get_opponent_actions(ai_position + 1 + num_players, ai_position + 2*num_players, num_players)

            for player, action in actions_after_ai:
                if action.startswith("fold"):
                    folded.add(player)
                elif action.startswith("call"):
                    pot += highest_bet - current_bets[player]
                    current_bets[player] = highest_bet
                elif action.startswith("raise"):
                    try:
                        amount = int(action.split()[1])
                    except:
                        print("Invalid raise amount. Skipping.")
                        continue
                    highest_bet = amount
                    current_bets[player] = amount
                    pot += amount
                ai.history.append(action.split()[0])

            if stage < 3:
                new_cards = parse_cards(input("Enter new community cards: "))
                community_cards.extend(new_cards)
            else:
                result = input("Did the AI win the hand? (y/n): ").strip().lower()
                if result == 'y':
                    ai.balance += pot
                    print(f"AI wins the pot! New balance: {ai.balance}")
                else:
                    print(f"AI loses the hand. Balance: {ai.balance}")
            stage += 1

if __name__ == "__main__":
    main()
