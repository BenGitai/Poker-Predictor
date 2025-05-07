public class PokerDraw {
    private int players;
    //private PokerPlayer[] playerArray;
    private double[] centerX = {0.3, 0.15, 0.15, 0.3,0.6,0.85,0.85,0.6};
    private double[] centerY = {0.1, 0.3, 0.6, 0.9,0.9,0.6,0.3,0.1};
    private int phase;
    private double cardXSize = (2.5 / 30);
    private double cardYSize = (3.5 / 30);
    private int cardDrawNum = 1;
    //private StdDraw draw = new StdDraw();
    public PokerDraw(int p){
        players = p;
        //playerArray = pa;
        StdDraw.setCanvasSize(400,400);
        StdDraw.clear(StdDraw.GREEN);
    }
    public void clear(){
        StdDraw.clear(StdDraw.GREEN);
    }
    public void setPhase(int p){
        phase = p;
    }
    public void paintCard(boolean up, int value1, String suit1, int value2, String suit2, int playerNum){
        String suitString1 = "";
        if (suit1.equals("Club")){
            suitString1 = "backClubs.png";
        }
        else if (suit1.equals("Diamond")){
            suitString1 = "backDiamonds.png";
        }
        else if (suit1.equals("Heart")){
            suitString1 = "backHearts.png";
        }
        else if (suit1.equals("Spade")){
            suitString1 = "backSpades.png";
        }
        
        String suitString2 = "";
        if (suit2.equals("Club")){
            suitString2 = "backClubs.png";
        }
        else if (suit2.equals("Diamond")){
            suitString2 = "backDiamonds.png";
        }
        else if (suit2.equals("Heart")){
            suitString2 = "backHearts.png";
        }
        else if (suit2.equals("Spade")){
            suitString2 = "backSpades.png";
        }
        if (up){
            if (playerNum >= 0){
                StdDraw.picture(centerX[playerNum] - (cardXSize/2), centerY[playerNum], suitString1, cardXSize, cardYSize);
                //StdDraw.rectangle(centerX[playerNum] - (cardXSize), centerY[playerNum], cardXSize, cardYSize);
                StdDraw.text(centerX[playerNum] - (cardXSize/2), centerY[playerNum], Integer.toString(value1));
                //StdDraw.text(centerX[playerNum] - (cardXSize), centerY[playerNum] - (cardYSize/2), suit1);

                StdDraw.picture(centerX[playerNum] + (cardXSize/2), centerY[playerNum], suitString2, cardXSize, cardYSize);
                //StdDraw.rectangle(centerX[playerNum] + (cardXSize), centerY[playerNum], cardXSize, cardYSize);
                StdDraw.text(centerX[playerNum] + (cardXSize/2), centerY[playerNum], Integer.toString(value2));
                //StdDraw.text(centerX[playerNum] + (cardXSize), centerY[playerNum] - (cardYSize/2), suit2);
            }
        }
        else{
            StdDraw.picture(centerX[playerNum] - (cardXSize/2), centerY[playerNum], "images.png", cardXSize, cardYSize);
            StdDraw.picture(centerX[playerNum] + (cardXSize/2), centerY[playerNum], "images.png",cardXSize, cardYSize);
        }
    }
    public boolean paintCard(boolean up, int value, String suit){
        String suitString = "";
        if (suit.equals("Club")){
            suitString = "backClubs.png";
        }
        else if (suit.equals("Diamond")){
            suitString = "backDiamonds.png";
        }
        else if (suit.equals("Heart")){
            suitString = "backHearts.png";
        }
        else if (suit.equals("Spade")){
            suitString = "backSpades.png";
        }
        double newCardX = 0.2 + (cardDrawNum * cardXSize);
        double newCardY = 0.5;
        StdDraw.picture(newCardX, newCardY, suitString, cardXSize, cardYSize);
        //StdDraw.rectangle(newCardX, newCardY, cardXSize, cardYSize);
        StdDraw.text(newCardX, newCardY, Integer.toString(value));
        //StdDraw.text(newCardX, newCardY - (cardYSize/2), suit);
        System.out.println("test");
        
        if (cardDrawNum >= 5){
            cardDrawNum = 1;
        } else{
            cardDrawNum += 1;
        }
        return true;
    }
}