public class PokerCalculator {
    private String[] activeSuits;
    private int[] activeValues;
    private String[] playerSuits;
    private int[] playerValues;

    public PokerCalculator(String[] as, int[] av, String[] ps, int[] pv){
        activeSuits = as;
        activeValues = av;
        playerSuits = ps;
        playerValues = pv;
    }
    public double cardProbability(int value){
        double chance = 0;
        for (int aValue : activeValues){
            if (aValue == value){
                chance += 1;
            }
        }
        chance /= playerValues.length;
        return chance;
    }
    public double cardProbability(String suit){
        double chance = 0;
        for (String aSuit : activeSuits){
            if (aSuit.equals(suit)){
                chance += 1;
            }
        }
        chance /= playerSuits.length;
        return chance;
    }
    public double cardProbability(int value, String suit){
        double chance = 0;
        for (int i = 0; i < playerValues.length; i++){
            if ((playerValues[i] == value) && (playerSuits[i].equals(suit))){
                chance += 1;
            }
        }
        chance /= playerValues.length;
        return chance;
    }
    public double onePairChance(){
        for (int i = 0; i < playerValues.length; i++){
            for (int j = i+1; j < playerValues.length; j++){
                if (playerValues[i] == playerValues[j]){
                    return 1;
                }
            }
        }
        double chance = 0;
        for (int pvalue : playerValues){
            double dup = 0;
            for (int avalue : activeValues){
                if (pvalue == avalue){
                    dup += 1;
                }
            }
            dup /= activeValues.length;
            chance += dup;
        }
        return chance;
    }
    public double twoPairChance(){
        double[] chances = new double[playerValues.length];
        for (int i = 0; i < playerValues.length; i++){
            double dup = 0;
            for (int avalue : activeValues){
                if (playerValues[i] == avalue){
                    dup += 1;
                }
            }
            dup /= activeValues.length;
            chances[i] = dup;
            for (int j = i+1; j < playerValues.length; j++){
                if (playerValues[i] == playerValues[j]){
                    chances[i] = 1;
                }
            }
        }
        double high1 = 0;
        double high2 = 0;

        for (double chance : chances){
            if (chance > high1){
                high1 = chance;
            }
            else if(chance > high2){
                high2 = chance;
            }
        }
        return (high1 * high2);
    }
    public double threeChance(){
        double chance = 0;
        for (int i = 0; i < playerValues.length; i++){
            int numVal = 1;
            boolean skip = false;
            for (int j = 0; j < i; j++){
                if (playerValues[i] == playerValues[j]){
                    skip = true;
                }
            }
            if (!skip){
                for (int j = i+1; j < playerValues.length; j++){
                    if (playerValues[i] == playerValues[j]){
                        numVal += 1;
                    }
                }
            }
            if (numVal >= 3){
                return 1;
            }
            else if (numVal == 2){
                double dup = 0;
                for (int avalue : activeValues){
                    if (playerValues[i] == avalue){
                        dup += 1;
                    }
                }
                dup /= activeValues.length;
                chance += dup;
            }
            else{
                double dup = 0;
                for (int avalue : activeValues){
                    if (playerValues[i] == avalue){
                        dup += 1;
                    }
                }
                dup /= activeValues.length;
                chance += (dup*dup);
            }
        }
        return chance;
    }
    public double fourChance(){
        double chance = 0;
        int numVal = 1;
        for (int i = 0; i < playerValues.length; i++){
            boolean skip = false;
            for (int j = 0; j < i; j++){
                if (playerValues[i] == playerValues[j]){
                    skip = true;
                }
            }
            if (!skip){
                for (int j = i+1; j < playerValues.length; j++){
                    if (playerValues[i] == playerValues[j]){
                        numVal += 1;
                    }
                }
            }
            double dup = 0;
            for (int avalue : activeValues){
                if (playerValues[i] == avalue){
                    dup += 1;
                }
            }
            dup /= activeValues.length;
            if (numVal >= 4){
                return 1;
            }
            else if (numVal == 3){
                chance += dup;
            }
            else if (numVal == 2){
                chance += (dup*dup);
            }
            else{
                chance += (dup*dup*dup);
            }
        }
        return chance;
    }
    public double straightChance(){
        double chance = 0;
        for (int i = 1; i <= 9; i++){
            double difficulty = 1;
            for (int j = i; j < i + 5; j++){
                int jvalue = j;
                if (j > 13){
                    jvalue = 1;
                }
                //System.out.println(jvalue);
                boolean has = false;
                for (int value : playerValues){
                    if (value == jvalue){
                        has = true;
                    }
                }
                //System.out.println(has);
                if (!has){
                    double dup = 0;
                    for (int avalue : activeValues){
                        if (jvalue == avalue){
                            dup += 1;
                        }
                    }
                    dup /= activeValues.length;
                    difficulty *= dup;
                    if (difficulty < 0.0001){
                        difficulty = 0;
                    }
                }
            }
            //System.out.println(i + ": " + difficulty);
            chance += difficulty;
        }
        if (chance < 1){
            return chance;
        }
        else{
            return 1;
        }
    }
    public double flushChance(){
        double chance = 0;
        String suit = "";
        for (int i = 0; i < 4; i++){
            int needed = 5;
            if (i == 0){
                suit = "Heart";
            }
            if (i == 1){
                suit = "Diamond";
            }
            if (i == 2){
                suit = "Spade";
            }
            if (i == 3){
                suit = "Club";
            }
            for (String psuit : playerSuits){
                if (psuit.equals(suit)){
                    needed -= 1;
                }
            }
            double dup = 0;
            for (String asuit : activeSuits){
                if (asuit.equals(suit)){
                    dup += 1;
                }
            }
            dup /= activeSuits.length;
            //System.out.println(suit + ": " + Math.pow(dup,needed));
            chance += Math.pow(dup, needed);
        }
        return chance;
    }
}
