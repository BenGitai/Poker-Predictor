public class PokerPlayer extends PlayGame{
    private int money;
    private int bet;
    private int players;
    private boolean fold;
    private int startMoney;
    private double[] winChance = {0.57734, 0.95246, 0.97887, 0.99975, 0.996075, 0.99803};
    public PokerPlayer(int p, String[] c, String[] s, int[] v, int m, PokerDraw d){
        super(c, s, v, d);
        money = m;
        players = p;
        startMoney = m;
    }
    public void bet(int b, Gamble pot){
        bet = b;
        money -= bet;
        pot.addBet(bet);
    }
    public void win(Gamble pot){
        int winnings = pot.getPot();
        money += winnings;
    }
    public int estimateBet(){
        double greatestPlayerChance = 0;
        double[] handChances = super.calculateChances();
        for (int i = 0; i < winChance.length; i++){
            double playerChance = handChances[i] * winChance[i];
            if (playerChance > greatestPlayerChance){
                greatestPlayerChance = playerChance;
            }
        }
        double greatestOppChance = 0;
        double[] oppChances = super.calculateOpponentChances();
        for (int i = 0; i < winChance.length; i++){
            double oppChance = oppChances[i] * winChance[i];
            if (oppChance > greatestOppChance){
                greatestOppChance = oppChance;
            }
        }
        double oppLose = 1 - greatestOppChance;
        oppLose = Math.pow(oppLose, players);
        double totalOppChance = 1 - oppLose;

        double chanceDiff = Math.pow(1 + greatestPlayerChance - totalOppChance, 2);
        if (chanceDiff < 0.3){
            return -1;
        }
        int standardBet = startMoney / 100;
        double totalChance = standardBet * chanceDiff;
        return (int)(totalChance + 1);
    }
    public void fold(boolean f, PokerPlayer[] pp){
        System.out.println("fold");
        fold = f;
        if (fold){
            for (PokerPlayer p : pp){
                p.players -= 1;
            }
        } else{
            for (PokerPlayer p : pp){
                p.players += 1;
            }
        }
    }
    public boolean foldStatus(){
        return fold;
    }
    public int getMoney(){
        return money;
    }
}
