public class Gamble {
    private int pot;
    private int minBet;
    public Gamble(){
        pot = 0;
    }
    public void addBet(int bet){
        pot += bet;
        if (bet > minBet){
            minBet = bet;
        }
    }
    public int getPot(){
        return pot;
    }
    public void clearPot(){
        pot = 0;
    }
    public int getminBet(){
        return minBet;
    }
    public void resetMinBet(){
        minBet = 0;
    }
    public int compare(PokerPlayer[] pp){
        int highestHand = -1;
        int highestHandPlayer = -1;
        int highestHandCard = -1;
        for (int i = 0; i < pp.length; i++){
            if (!pp[i].foldStatus()){
                int highHand = -1;
                double[] outcomes = pp[i].calculateChances();
                for (int j = 0; j < outcomes.length; j++){
                    if (outcomes[j] == 1.0){
                        highHand = j;
                    }
                }
                if (highestHand < highHand){
                    highestHand = highHand;
                    highestHandPlayer = i;
                } else if (highHand == highestHand){
                    int highPlayerCard = 0;
                    for (int card : pp[i].getPlayerValues()){
                        if (card > highPlayerCard){
                            highPlayerCard = card;
                        }
                    }
                    if (highPlayerCard > highestHandCard){
                        highestHandCard = highPlayerCard;
                        highestHandPlayer = i;
                    }
                }
            }
        }
        return highestHandPlayer;
        
    }
}
