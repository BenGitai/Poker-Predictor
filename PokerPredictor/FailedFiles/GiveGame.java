import java.util.ArrayList;

public class GiveGame {
    private String[] cards;
    private String[] suits;
    private int[] values;

    private ArrayList<String> activeCards = new ArrayList<>();
    private ArrayList<String> activeSuits = new ArrayList<>();
    private ArrayList<Integer> activeValues = new ArrayList<>();

    private ArrayList<String> playerCards = new ArrayList<>();
    private ArrayList<String> playerSuits = new ArrayList<>();
    private ArrayList<Integer> playerValues = new ArrayList<>();

    private ArrayList<String> tableCards = new ArrayList<>();
    private ArrayList<String> tableSuits = new ArrayList<>();
    private ArrayList<Integer> tableValues = new ArrayList<>();
    //private PokerDraw draw;

    public GiveGame(String[] c, String[] s, int[] v, PokerDraw d){
        cards = c;
        suits = s;
        values = v;
        for (String card : cards){
            activeCards.add(card);
            //System.out.print(card + ", ");
        }
        System.out.println();
        for (String suit : suits){
            activeSuits.add(suit);
        }
        for (int value : values){
            activeValues.add(value);
        }
        //draw = d;
    }
    public void shuffle(){
        for (String card : cards){
            activeCards.add(card);
        }
        for (String suit : suits){
            activeSuits.add(suit);
        }
        for (int value : values){
            activeValues.add(value);
        }
    }
    public int findCard(String suit, int value){
        for (int i = 0; i < activeCards.size(); i++){
            if ((activeSuits.get(i).equals(suit)) && (activeValues.get(i) == value)){
                return i;
            }
        }
        return -1;
    }
    public void givePlayerCard(int cardNum){
        playerCards.add(activeCards.remove(cardNum));
        playerSuits.add(activeSuits.remove(cardNum));
        playerValues.add(activeValues.remove(cardNum));
    }

    public void giveTableCard(int cardNum){
        playerCards.add(activeCards.get(cardNum));
        playerSuits.add(activeSuits.get(cardNum));
        playerValues.add(activeValues.get(cardNum));

        tableCards.add(playerCards.get(playerCards.size()-1));
        tableSuits.add(playerSuits.get(playerSuits.size()-1));
        tableValues.add(playerValues.get(playerValues.size()-1));

        //draw.paintCard(true, playerValues.get(playerValues.size()-1), playerSuits.get(playerSuits.size()-1));
    }

    public void clearPlayerCards(){
        while (playerCards.size() > 0){
            playerCards.remove(0);
            playerSuits.remove(0);
            playerValues.remove(0);
        }
    }

    public String[] showPlayerCards(){
        String[] pc = new String[playerCards.size()];
        for (int i = 0; i < playerCards.size(); i++){
            pc[i] = playerCards.get(i);
        }
        return pc;
    }

    public int[] getPlayerValues(){
        int[] pv = new int[playerValues.size()];
        for (int i = 0; i < playerValues.size(); i++){
            pv[i] = playerValues.get(i);
        }
        return pv;
    }

    public String[] getPlayerSuits(){
        String[] ps = new String[playerSuits.size()];
        for (int i = 0; i < playerSuits.size(); i++){
            ps[i] = playerSuits.get(i);
        }
        return ps;
    }

    public double[] calculateChances(){
        double[] chances = new double[6];

        String[] as = new String[activeSuits.size()];
        int[] av = new int[activeSuits.size()];
        String[] ps = new String[playerSuits.size()];
        int[] pv = new int[playerSuits.size()];

        for (int i = 0; i < activeSuits.size(); i++){
            as[i] = activeSuits.get(i);
            av[i] = activeValues.get(i);
        }
        for (int i = 0; i < playerSuits.size(); i++){
            ps[i] = playerSuits.get(i);
            pv[i] = playerValues.get(i);
        }

        PokerCalculator calculator = new PokerCalculator(as, av, ps, pv);

        chances[0] = calculator.onePairChance();
        chances[1] = calculator.twoPairChance();
        chances[2] = calculator.threeChance();
        chances[3] = calculator.fourChance();
        chances[4] = calculator.straightChance();
        chances[5] = calculator.flushChance();

        return chances;
    }
    public double[] calculateOpponentChances(){
        double[] chances = new double[6];

        String[] as = new String[activeSuits.size()];
        int[] av = new int[activeSuits.size()];
        String[] ts = new String[tableSuits.size()];
        int[] tv = new int[tableSuits.size()];

        for (int i = 0; i < activeSuits.size(); i++){
            as[i] = activeSuits.get(i);
            av[i] = activeValues.get(i);
        }
        for (int i = 0; i < tableSuits.size(); i++){
            ts[i] = tableSuits.get(i);
            tv[i] = tableValues.get(i);
        }

        PokerCalculator calculator = new PokerCalculator(as, av, ts, tv);

        chances[0] = calculator.onePairChance();
        chances[1] = calculator.twoPairChance();
        chances[2] = calculator.threeChance();
        chances[3] = calculator.fourChance();
        chances[4] = calculator.straightChance();
        chances[5] = calculator.flushChance();

        return chances;
    }
    public int getDeckSize(){
        return activeCards.size();
    }
    public void removeCard (int cardNum){
        activeCards.remove(cardNum);
        activeSuits.remove(cardNum);
        activeValues.remove(cardNum);
    }
}
