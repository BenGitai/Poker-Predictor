import java.util.*;
public class PlayGame extends GiveGame{
    
    public PlayGame(String[] c, String[] s, int[] v, PokerDraw d){
        super(c, s, v, d);
    }
    public void dealPlayer(){
        int randomCard = (int)(Math.random() * super.getDeckSize());
        super.givePlayerCard(randomCard);        
    }
    public void dealTable(int cardNum){
        super.giveTableCard(cardNum);
    }
    
}
