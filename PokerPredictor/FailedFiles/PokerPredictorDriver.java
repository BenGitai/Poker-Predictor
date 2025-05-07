import java.util.*;
public class PokerPredictorDriver{
    public static void main(String[] args) {
        //Give intro and prompt for play game or give game
        System.out.println("(play/give)");
        Scanner input = new Scanner(System.in);
        boolean playGame = (input.next().equals("play"));

        System.out.println("Number of Players");
        int players = input.nextInt();


        System.out.println("Number of Decks");
        int decks = input.nextInt();

        String[] cards = new String[decks * 52];
        int[] values = new int[decks * 52];
        String[] suits = new String[decks * 52];

        for (int i = 0; i < decks; i++){
            for (int j = 1; j <= 13; j++){
                values[i*52 + ((j-1)*4)] = j;
                values[i*52 + ((j-1)*4) + 1] = j;
                values[i*52 + ((j-1)*4) + 2] = j;
                values[i*52 + ((j-1)*4) + 3] = j;

                suits[i*52 + ((j-1)*4)] = "Heart";
                suits[i*52 + ((j-1)*4) + 1] = "Diamond";
                suits[i*52 + ((j-1)*4) + 2] = "Spade";
                suits[i*52 + ((j-1)*4) + 3] = "Club";

                String name = "";
                if (j == 1){
                    name += "Ace";
                }
                else if(j == 11){
                    name += "Jack";
                }
                else if(j == 12){
                    name += "Queen";
                }
                else if(j == 13){
                    name += "King";
                }
                else{
                    name += Integer.toString(j);
                }

                name += " of ";

                cards[i*52 + ((j-1)*4)] = name + "Hearts";
                cards[i*52 + ((j-1)*4) + 1] = name + "Diamonds";
                cards[i*52 + ((j-1)*4) + 2] = name + "Spades";
                cards[i*52 + ((j-1)*4) + 3] = name + "Clubs";

            }
        }
        PokerPlayer[] playerArray = new PokerPlayer[players];
        PokerDraw draw = new PokerDraw(players);
        for (int i = 0; i < playerArray.length; i++){
            playerArray[i] = new PokerPlayer(players, cards, suits, values, 1000, draw);
        }
        boolean play = true;

        while(!playGame){
            System.out.println("\nGive player card or calculate or clear hand or show hand (give/calculate/clear/show)");
            String choice = input.next();
            if (choice.equals("give")){
                System.out.println("What value card?");
                int value = input.nextInt();
                System.out.println("What suit card?");
                String suit = input.next();
                int cardNum = playerArray[0].findCard(suit, value);
                System.out.println(cardNum);
                if (cardNum != -1){
                    playerArray[0].givePlayerCard(cardNum);
                }
            }
            if (choice.equals("calculate")){
                double[] chances = playerArray[0].calculateChances();
                for (double chance : chances){
                    System.out.println(chance);
                }

            }
            if (choice.equals("clear")){
                playerArray[0].clearPlayerCards();
            }
            if (choice.equals("show")){
                String[] pc = playerArray[0].showPlayerCards();
                for (String card : pc){
                    System.out.println(card);
                }
            }
        }
        int phase = 1;
        Gamble pot = new Gamble();
        while (play){
            System.out.println("Choices: deal, show, calculate, shuffle, clear, bet, fold, leave");
            String choice = input.next();
            if (choice.equals("deal")){
                System.out.println(phase);
                if (phase == 1){
                    draw.clear();
                    int playerNumber = 0;
                    for (PokerPlayer player : playerArray){
                        player.dealPlayer();
                        player.dealPlayer();
                        boolean up = (playerNumber == 0);
                        draw.paintCard(up, player.getPlayerValues()[0], player.getPlayerSuits()[0], player.getPlayerValues()[1], player.getPlayerSuits()[1], playerNumber);
                        playerNumber += 1;
                    }
                    phase = 2;
                } else if (phase == 2){
                    int randomCard1 = (int)(Math.random() * playerArray[0].getDeckSize());
                    int randomCard2 = (int)(Math.random() * playerArray[0].getDeckSize()) - 1;
                    int randomCard3 = (int)(Math.random() * playerArray[0].getDeckSize()) - 2;
                    for (PokerPlayer player : playerArray){
                        player.dealTable(randomCard1);
                        //draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-1], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-1]);
                        player.dealTable(randomCard2);
                        //draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-1], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-1]);
                        player.dealTable(randomCard3);
                        //draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-1], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-1]);
                    }
                    draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-3], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-3]);
                    draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-2], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-2]);
                    draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-1], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-1]);
                    for (PokerPlayer player : playerArray){    
                        player.removeCard(randomCard1);
                        if (randomCard1 < randomCard2){
                            randomCard2 -= 1;
                        }
                        player.removeCard(randomCard2);

                        if (randomCard2 < randomCard3){
                            randomCard3 -= 1;
                        }
                        
                        if (randomCard1 < randomCard3){
                            randomCard3 -= 1;
                        }
                        
                        player.removeCard(randomCard3);
                    }

                    phase = 3;
                } else if (phase == 3){
                    int randomCard = (int)(Math.random() * playerArray[0].getDeckSize());
                    for (PokerPlayer player : playerArray){
                        player.dealTable(randomCard);
                        //draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-1], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-1]);
                    }
                    draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-1], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-1]);
                    for (PokerPlayer player : playerArray){
                        player.removeCard(randomCard);
                    }

                    phase = 4;
                    
                } else if (phase == 4){
                    int randomCard = (int)(Math.random() * playerArray[0].getDeckSize());
                    for (PokerPlayer player : playerArray){
                        player.dealTable(randomCard);
                        //draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-1], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-1]);
                    }
                    draw.paintCard(true, playerArray[0].getPlayerValues()[playerArray[0].getPlayerValues().length-1], playerArray[0].getPlayerSuits()[playerArray[0].getPlayerSuits().length-1]);
                    for (PokerPlayer player : playerArray){
                        player.removeCard(randomCard);
                    }
                    phase = 5;
                    System.out.println("All Cards Dealt, Next Deal Ends Round");
                } else if (phase == 5){
                    
                    for (int i = 0; i < playerArray.length; i++){
                        draw.paintCard(true, playerArray[i].getPlayerValues()[0], playerArray[i].getPlayerSuits()[0], playerArray[i].getPlayerValues()[1], playerArray[i].getPlayerSuits()[1], i);
                    }

                    int winner = pot.compare(playerArray);

                    System.out.println("The Winner is Player " + winner);

                    playerArray[winner].win(pot);

                    String[] winningCards = playerArray[winner].showPlayerCards();

                    for (String card : winningCards){
                        System.out.println(card);
                    }

                    phase = 1;
                    pot.clearPot();
                    for (PokerPlayer p : playerArray){
                        p.clearPlayerCards();
                        p.fold(false, playerArray);
                    }
                }
            }
            else if(choice.equals("show")){
                String[] pCards = playerArray[0].showPlayerCards();
                for (String card : pCards){
                    System.out.println(card);
                }
                System.out.println("Pot: " + pot.getPot());
                System.out.println("Money: " + playerArray[0].getMoney());
            }
            else if(choice.equals("calculate")){
                double[] playerChance = playerArray[0].calculateChances();
                for (double chance : playerChance){
                    System.out.println(chance);
                }
                System.out.println(playerArray[0].estimateBet());
            }
            else if(choice.equals("shuffle")){
                for (PokerPlayer player : playerArray){
                    player.shuffle();
                }
            }
            else if(choice.equals("clear")){
                for (PokerPlayer player : playerArray){
                    player.shuffle();
                }
            }
            else if(choice.equals("bet")){
                boolean betting = true;
                pot.resetMinBet();
                while (betting){
                    boolean validBet = false;
                    int bet = 0;
                    while (!validBet){
                        System.out.print("Betting Amount: ");
                        bet = input.nextInt();
                        if (bet >= pot.getminBet()){
                            validBet = true;
                        } 
                        else if (bet < 0){
                            playerArray[0].fold(true, playerArray);
                            phase = 5;
                            validBet = true;
                            betting = false;
                            System.out.println("fold");
                        }
                        else{
                            System.out.println("That Is Not A Valid Bet");
                        }
                    }
                    playerArray[0].bet(bet, pot);
                    for (int i = 1; i < playerArray.length; i++){
                        if (!playerArray[i].foldStatus()){
                            int oppBet = playerArray[i].estimateBet();
                            if (oppBet > 0){
                                if (oppBet < pot.getminBet()){
                                    if (oppBet < pot.getminBet() / 3){
                                        playerArray[i].fold(true, playerArray);
                                    }
                                    else{
                                        oppBet = pot.getminBet();
                                        playerArray[i].bet(oppBet, pot);
                                    }
                                }
                                else{
                                    playerArray[i].bet(oppBet, pot);
                                }
                                System.out.println("Player " + i + " bets: "+ oppBet);
                            }
                            else{
                                playerArray[i].fold(true, playerArray);
                            }
                        }
                    }
                    if (bet >= pot.getminBet()){
                        betting = false;
                    }
                    else if (bet < 0){
                        playerArray[0].fold(true, playerArray);
                        phase = 5;
                        validBet = true;
                        betting = false;
                        System.out.println("fold");
                    }
                }
            }
            else if(choice.equals("fold")){
                playerArray[0].fold(true, playerArray);
                phase = 5;
            }
            else if(choice.equals("leave")){
                play = false;
                System.out.println("Final Take Away: " + playerArray[0].getMoney());
                System.out.println("Net: " + (playerArray[0].getMoney() - 1000));
            }
        }
        //PokerCalculator testCalculator = new PokerCalculator(players, cards, values, suits, values);
        /*
         * Things to add/change:
         * Make the input system modular and have the cards dealt be the only bit that changes
         * Create betting/suggested betting system
         * Allow for more players (both people and COM)
         */
    }
}