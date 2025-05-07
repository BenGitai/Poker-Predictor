import random
from Poker2 import PokerAI, BotPlayer

RANKS = "23456789TJQKA"
SUITS = "SHDC"

STAGES = ["Pre-Flop", "Flop", "Turn", "River"]

def create_deck():
    deck = [r + s for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

def get_player_action(player_name, highest_bet):
    while True:
        action = input(f"{player_name}'s action (fold/call/raise amount): ").strip().lower()
        if action.startswith("fold"):
            return ("fold", 0)
        elif action.startswith("call"):
            return ("call", highest_bet)
        elif action.startswith("raise"):
            parts = action.split()
            if len(parts) == 2 and parts[1].isdigit():
                return ("raise", int(parts[1]))
        print("Invalid input. Try again.")

def evaluate_hand_strength(hand, community):
    # Dummy evaluation by assigning score from highest card
    all_cards = hand + community
    return max(RANKS.index(card[0]) for card in all_cards)

def play_poker_game(num_ai, num_bots):
    players = []
    total_players = num_ai + num_bots + 1  # Include human player

    for i in range(num_ai):
        players.append(PokerAI(name=f"Player_{i+1}", save_file=f"AI_{i+1}.json"))
    for i in range(num_bots):
        players.append(BotPlayer(name=f"Player_{num_ai+i+1}"))
    players.append("HUMAN")
    random.shuffle(players)

    balances = {f"Player_{i+1}": 1000 for i in range(total_players)}

    round_number = 1
    while True:
        print(f"\n========== Round {round_number} ==========")
        pot = 0
        highest_bet = 0
        folded = set()
        hole_cards = {}
        community_cards = []

        deck = create_deck()

        for i, player in enumerate(players):
            name = f"Player_{i+1}"
            hand = [deck.pop(), deck.pop()]
            hole_cards[name] = hand
            if isinstance(player, PokerAI):
                player.hand = hand

        print("\n--- Hole Cards Dealt ---")
        for i, player in enumerate(players):
            name = f"Player_{i+1}"
            if player == "HUMAN":
                print(f"Your hole cards: {' '.join(hole_cards[name])}")

        for stage_index, stage in enumerate(STAGES):
            print(f"\n--- {stage} ---")

            if stage == "Flop":
                community_cards += [deck.pop(), deck.pop(), deck.pop()]
            elif stage in ["Turn", "River"]:
                community_cards.append(deck.pop())

            if stage != "Pre-Flop":
                print(f"Community Cards: {' '.join(community_cards)}")

            current_bets = {name: 0 for name in balances}

            for i, player in enumerate(players):
                name = f"Player_{i+1}"
                if name in folded:
                    continue

                if player == "HUMAN":
                    action, amount = get_player_action(name, highest_bet)
                elif isinstance(player, PokerAI):
                    player.update_win_probability(0.5)  # Placeholder
                    amount = player.decide_bet(highest_bet, min_raise=0, total_pot=pot, betting_stage=stage_index)
                    action = "fold" if amount == 0 else "raise" if amount > highest_bet else "call"
                    print(f"{name} (AI) decides to {action} {amount if action == 'raise' else ''}".strip())
                else:
                    amount = player.decide_bet(0.5, highest_bet, pot, stage_index)
                    action = "fold" if amount == 0 else "raise" if amount > highest_bet else "call"
                    print(f"{name} (Bot) decides to {action} {amount if action == 'raise' else ''}".strip())

                if action == "fold":
                    folded.add(name)
                else:
                    pot += amount
                    balances[name] -= amount
                    current_bets[name] = amount
                    if amount > highest_bet:
                        highest_bet = amount

        print("\n--- Showdown ---")
        active_players = [f"Player_{i+1}" for i in range(len(players)) if f"Player_{i+1}" not in folded]

        if not active_players:
            print("Everyone folded! No winner.")
        else:
            strengths = {
                name: evaluate_hand_strength(hole_cards[name], community_cards)
                for name in active_players
            }
            winner = max(strengths, key=strengths.get)
            balances[winner] += pot
            print(f"{winner} wins the pot of {pot} chips!")

        print("\n--- End of Hand ---")
        print("Player Balances:")
        for name, bal in balances.items():
            print(f"{name}: {bal} chips")

        cont = input("\nPlay another round? (y/n): ").strip().lower()
        if cont != 'y':
            break
        round_number += 1

if __name__ == "__main__":
    num_ai = int(input("Number of AI players: "))
    num_bots = int(input("Number of Bot players: "))
    play_poker_game(num_ai, num_bots)
