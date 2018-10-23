package javaapplication85;

import java.util.ArrayList;
import java.util.InputMismatchException;
import java.util.Scanner;

public class Piskvorky1krat1komplet {

    public static void main(String[] args) {
        // TODO code application logic here
        // INITIALIZING ARRAYS TO STORE MOVES
        int[] letters = new int[200], numbers = new int[200], letters2 = new int[200], numbers2 = new int[200];
        for (int i = 0; i < 200; i++) {
            letters[i] = -1;
            numbers[i] = -1;
            letters2[i] = -1;
            numbers2[i] = -1;
        }

        ArrayList<String> player1Coord = new ArrayList<>();
        ArrayList<String> player2Coord = new ArrayList<>();

        ArrayList<Integer> p1code = new ArrayList<>();
        ArrayList<Integer> p2code = new ArrayList<>();

        ArrayList<Integer> p1n = new ArrayList<>(); //player 1 numbers
        ArrayList<Integer> p1l = new ArrayList<>(); //player 1 letters
        ArrayList<Integer> p2n = new ArrayList<>(); //player 2 numbers
        ArrayList<Integer> p2l = new ArrayList<>(); //player 2 letters

        String g = "abcdefghijklmnopqrstuvwxyz";

        Scanner input = new Scanner(System.in);
        System.out.print("Please enter the name of the first player: ");
        String p1 = input.nextLine();
        System.out.print(p1 + ", please choose your symbol: ");
        String c1 = input.nextLine();

        if (c1.length() != 1) {
            System.out.print("ERROR: You must enter only one character!");
            c1 = input.nextLine();
        }

        if (c1.length() != 1) {
            System.out.println("ERROR: You do not follow the rules, you will play with X!");
            c1 = "X";
        }

        System.out.print("Please enter the name of the second player: ");
        String p2 = input.nextLine();
        System.out.print(p2 + ", please choose your symbol: ");
        String c2 = input.nextLine();

        if (c2.length() != 1) {
            System.out.println("ERROR: You must enter only one character!");
            c2 = input.nextLine();
        }

        if (c2.length() != 1) {
            System.out.println("ERROR: You do not follow the rules, you will play with O!");
            c2 = "O";
        }

        System.out.print("Please enter the size of the board: ");

        int q = input.nextInt();
        while (q > 26 || q < 2) {
            System.out.print("Sorry, only number between 2 and 26 can be chosen. Choose again: ");
            q = input.nextInt();
        }
        /*
        try {
        q = input.nextInt();
        }
        catch (Exception e) {
            System.out.println("ERROR: You did not enter right format. Try again! ");
        }
         */

 /*
        while (SettingTheBoard.isInteger(g) == false || q > 20 || qw) {
            try {
        q = input.nextInt();
        }
        catch (Exception e) {
            System.out.println("ERROR: You did not enter right format. Try again! ");
        }
        }
      
        /*
        while (q > 9) {
            System.out.print("Sorry, only sizes of 9 or less are supported. Choose size again: ");
               q = input.nextInt();
        }
         */
        System.out.print("Choose number of the winning rows: ");
        int n = input.nextInt();

        while (n > 5 || n < 2) {
            System.out.print("Sorry, only number between 2 and 5 can be chosen. Choose again: ");
            n = input.nextInt();
        }

        int x = 2 * q + 1;

        System.out.println("");

        SettingTheBoard.letters(x);

        System.out.println("");

        for (int i = 0; i < x; i++) {

            for (int j = -1; j < x; j++) {

                if (i % 2 == 0 && j != -1 || j % 2 == 0) {
                    System.out.print("* ");
                } else if (j == -1 && i % 2 == 1) {
                    int e = (i + 1) / 2;
                    int ee = q + 1 - e;
                    if (Integer.toString(ee).length() > 1) {
                        System.out.print(ee);
                    } else {
                        System.out.print(ee + " ");
                    }
                } else {
                    System.out.print("  ");
                }
            }

            SettingTheBoard.numbers(i, q);

            System.out.println("");
        }

        SettingTheBoard.letters(x);

        System.out.println("");
        System.out.println("");

        // MAKING MOVES
        for (int d = 0; d < q * q; d++) {

            /////////////////////////////////////  
            // FIRST PLAYER STARTS
            /////////////////////////////////////////
            System.out.println(p1 + ", it's your move!");

            if (d == 0) {
                input.nextLine();
            }

            // GETTING A COORDINATION
            String s = input.nextLine();

            // QUIT FUNCTION
            if (s.equals("quit")) {
                break;
            }

            if (s.equals("give up")) {
                System.out.println("------------------------------------");
                System.out.println(p2 + " won. Congratulation!!!");
                System.out.println("------------------------------------");
                break;
            } /////////////////////////////////////
            // MAIN VARIATION STARTS
            //////////////////////////////////////
            else {

                int first = 0;
                int second = 0;
                String s1 = "";
                String s2 = "";

                try {

                    s1 = s.substring(0, 1).toLowerCase();
                    s2 = s.substring(1);

                    g = "abcdefghijklmnopqrstuvwxyz";
                    first = g.indexOf(s1) + 1;
                    second = Integer.parseInt(s2);
                } catch (Exception e) {
                    // System.out.println(e.getMessage());
                }

                boolean alreadythere = (player1Coord.contains(s) || player2Coord.contains(s));
                boolean badformat = (SettingTheBoard.isInteger(s1) == true || SettingTheBoard.isInteger(s2) == false);
                boolean unexistedcoord = (first > q || second > q);

                // DEFENCE AGAINST BAD FORMATS
                while (alreadythere == true || badformat == true || unexistedcoord == true) {

                    if (alreadythere == true) {
                        System.out.println("ERROR: The coordination " + s1 + s2 + " is already ocupied. Try again! ");
                    }

                    if (badformat == true) {
                        System.out.println("ERROR: You did not enter coordination in the right format. Try again! ");
                    }

                    if (unexistedcoord == true) {
                        System.out.print("ERROR: The coordination " + s1 + s2 + " doesn't exist. Try again! ");
                    }

                    try {
                        s = input.nextLine();
                        s1 = s.substring(0, 1).toLowerCase();
                        s2 = s.substring(1);

                        g = "abcdefghijklmnopqrstuvwxyz";
                        first = g.indexOf(s1) + 1;
                        second = Integer.parseInt(s2);
                    } catch (Exception e) {

                    }

                    alreadythere = (player1Coord.contains(s) || player2Coord.contains(s));
                    badformat = (SettingTheBoard.isInteger(s1) == true || SettingTheBoard.isInteger(s2) == false);
                    unexistedcoord = (first > q || second > q);
                }

                // ASSIGNING LETTER
                int l = g.indexOf(s1);
                int h = 1 + 2 * l;
                letters[d] = h;

                // ASSIGNING NUMBER
                int k = Integer.parseInt(s2);
                int r = x - (2 * k);
                numbers[d] = r;

                player1Coord.add(s);
                p1n.add(r);
                p1l.add(h);

                // MAKING THE BOARD
                System.out.println("");

                SettingTheBoard.letters(x);

                System.out.println("");

                for (int i = 0; i < x; i++) {

                    for (int j = -1; j < x; j++) {
                        /*     int int1 = 0;
                try {
                String string1 = Integer.toString(i) + Integer.toString(j);
                 int1 = Integer.parseInt(string1); 
                }
                catch (Exception e) {
                    
                }
                         */
                        if (i % 2 == 0 && j != -1 || j % 2 == 0) {
                            System.out.print("* ");
                        } else if (j == -1 && i % 2 == 1) {
                            int e = (i + 1) / 2;
                            int ee = q + 1 - e;
                            if (ee > 9) {
                                System.out.print(ee);
                            } else {
                                System.out.print(ee + " ");
                            }
                        } else if (i == numbers[0] && j == letters[0] || i == numbers[1] && j == letters[1] || i == numbers[2] && j == letters[2] || i == numbers[3] && j == letters[3] || i == numbers[4] && j == letters[4] || i == numbers[5] && j == letters[5] || i == numbers[6] && j == letters[6] || i == numbers[7] && j == letters[7] || i == numbers[8] && j == letters[8] || i == numbers[9] && j == letters[9] || i == numbers[10] && j == letters[10] || i == numbers[11] && j == letters[11] || i == numbers[12] && j == letters[12] || i == numbers[13] && j == letters[13] || i == numbers[14] && j == letters[14] || i == numbers[15] && j == letters[15] || i == numbers[16] && j == letters[16] || i == numbers[17] && j == letters[17] || i == numbers[18] && j == letters[18] || i == numbers[19] && j == letters[19] || i == numbers[20] && j == letters[20] || i == numbers[21] && j == letters[21] || i == numbers[22] && j == letters[22] || i == numbers[23] && j == letters[23] || i == numbers[24] && j == letters[24] || i == numbers[25] && j == letters[25] || i == numbers[26] && j == letters[26] || i == numbers[27] && j == letters[27] || i == numbers[28] && j == letters[28] || i == numbers[29] && j == letters[29] || i == numbers[30] && j == letters[30] || i == numbers[31] && j == letters[32]) {
                            System.out.print(c1 + " ");
                        } else if (i == numbers2[0] && j == letters2[0] || i == numbers2[1] && j == letters2[1] || i == numbers2[2] && j == letters2[2] || i == numbers2[3] && j == letters2[3] || i == numbers2[4] && j == letters2[4] || i == numbers2[5] && j == letters2[5] || i == numbers2[6] && j == letters2[6] || i == numbers2[7] && j == letters2[7] || i == numbers2[8] && j == letters2[8] || i == numbers2[9] && j == letters2[9] || i == numbers2[10] && j == letters2[10] || i == numbers2[11] && j == letters2[11] || i == numbers2[12] && j == letters2[12] || i == numbers2[13] && j == letters2[13] || i == numbers2[14] && j == letters2[14] || i == numbers2[15] && j == letters2[15] || i == numbers2[16] && j == letters2[16] || i == numbers2[17] && j == letters2[17] || i == numbers2[18] && j == letters2[18] || i == numbers2[19] && j == letters2[19] || i == numbers2[20] && j == letters2[20] || i == numbers2[21] && j == letters2[21] || i == numbers2[22] && j == letters2[22] || i == numbers2[23] && j == letters2[23] || i == numbers2[24] && j == letters2[24] || i == numbers2[25] && j == letters2[25] || i == numbers2[26] && j == letters2[26] || i == numbers2[27] && j == letters2[27] || i == numbers2[28] && j == letters2[28] || i == numbers2[29] && j == letters2[29] || i == numbers2[30] && j == letters2[30] || i == numbers2[31] && j == letters2[32]) {
                            System.out.print(c2 + " ");
                        } else {
                            System.out.print("  ");
                        }
                    }

                    SettingTheBoard.numbers(i, q);

                    System.out.println("");
                }

                SettingTheBoard.letters(x);

                System.out.println("");
                System.out.println("");

            }

            //////////////////////////////////
            ////// EVALUATION OF THE WINNER
            ///////////////////////////////
            for (int i = 0; i <= d; i++) {

                String s1 = player1Coord.get(i).substring(0, 1);
                String s2 = player1Coord.get(i).substring(1);

                // ASSIGNING LETTER
                int l = g.indexOf(s1) + 1;

                // ASSIGNING NUMBER
                int k = Integer.parseInt(s2);

                int a = l * 10 + k;

                p1code.add(a);
            }

            p1code.sort(null);

            int quit = 0;

            if (n == 2) {
                for (int i = 0; i < d; i++) {
                    int gg = p1code.get(i);
                    boolean b1 = p1code.contains(gg + 1);
                    boolean b2 = p1code.contains(gg + 9);
                    boolean b3 = p1code.contains(gg + 10);
                    boolean b4 = p1code.contains(gg + 11);

                    if (b1 || b2 || b3 || b4) {
                        System.out.println("--------------------------------------------------");
                        System.out.println(p1 + " won. Congratulation!!!");
                        System.out.println("--------------------------------------------------");

                        quit++;
                        break;
                    }
                }
            }

            if (n == 3) {

                for (int i = 0; i < d; i++) {
                    int gg = p1code.get(i);
                    boolean b1 = p1code.contains(gg + 1) && p1code.contains(gg + 2);
                    boolean b2 = p1code.contains(gg + 9) && p1code.contains(gg + 18);
                    boolean b3 = p1code.contains(gg + 10) && p1code.contains(gg + 20);
                    boolean b4 = p1code.contains(gg + 11) && p1code.contains(gg + 22);

                    if (b1 || b2 || b3 || b4) {
                        System.out.println("--------------------------------------------------");
                        System.out.println(p1 + " won. Congratulation!!!");
                        System.out.println("--------------------------------------------------");

                        quit++;
                        break;
                    }
                }

            }

            if (n == 4) {
                for (int i = 0; i < d; i++) {
                    int gg = p1code.get(i);
                    boolean b1 = p1code.contains(gg + 1) && p1code.contains(gg + 2) && p1code.contains(gg + 3);
                    boolean b2 = p1code.contains(gg + 9) && p1code.contains(gg + 18) && p1code.contains(gg + 27);
                    boolean b3 = p1code.contains(gg + 10) && p1code.contains(gg + 20) && p1code.contains(gg + 30);
                    boolean b4 = p1code.contains(gg + 11) && p1code.contains(gg + 22) && p1code.contains(gg + 33);

                    if (b1 || b2 || b3 || b4) {
                        System.out.println("--------------------------------------------------");
                        System.out.println(p1 + " won. Congratulation!!!");
                        System.out.println("--------------------------------------------------");

                        quit++;
                        break;
                    }
                }
            }

            if (n == 5) {
                for (int i = 0; i < d; i++) {
                    int gg = p1code.get(i);
                    boolean b1 = p1code.contains(gg + 1) && p1code.contains(gg + 2) && p1code.contains(gg + 3) && p1code.contains(gg + 4);
                    boolean b2 = p1code.contains(gg + 9) && p1code.contains(gg + 18) && p1code.contains(gg + 27) && p1code.contains(gg + 36);
                    boolean b3 = p1code.contains(gg + 10) && p1code.contains(gg + 20) && p1code.contains(gg + 30) && p1code.contains(gg + 40);
                    boolean b4 = p1code.contains(gg + 11) && p1code.contains(gg + 22) && p1code.contains(gg + 33) && p1code.contains(gg + 44);

                    if (b1 || b2 || b3 || b4) {
                        System.out.println("--------------------------------------------------");
                        System.out.println(p1 + " won. Congratulation!!!");
                        System.out.println("--------------------------------------------------");

                        quit++;
                        break;
                    }
                }
            }

            if (quit > 0) {
                break;
            }

            // SECOND PLAYER STARTS
            System.out.println(p2 + ", it's your move!");

            String z = input.nextLine();

            if (z.equals("quit")) {
                break;
            }

            if (s.equals("give up")) {
                System.out.println("------------------------------------");
                System.out.println(p1 + " won. Congratulation!!!");
                System.out.println("------------------------------------");
                break;
            }

            if (z.equals("back")) {
                letters[d] = -1;
                numbers[d] = -1;

            } ////////////////////////////////////////////
            // MAIN VARIATION PLAYER2
            ////////////////////////////////////////////////
            else {

                int first2 = 0;
                int second2 = 0;
                String z1 = "";
                String z2 = "";

                try {
                    z1 = z.substring(0, 1).toLowerCase();
                    z2 = z.substring(1);
                    g = "abcdefghijklmnopqrstuvwxyz";
                    first2 = g.indexOf(z1) + 1;
                    second2 = Integer.parseInt(z2);
                } catch (NumberFormatException e) {
                    // System.out.println(e.getMessage());
                }

                boolean alreadythere2 = (player1Coord.contains(z) || player2Coord.contains(z));
                boolean badformat2 = (SettingTheBoard.isInteger(z1) == true || SettingTheBoard.isInteger(z2) == false);
                boolean unexistedcoord2 = (first2 > q || second2 > q);

                // DEFENCE AGAINST BAD FORMATS
                while (alreadythere2 == true || badformat2 == true || unexistedcoord2 == true) {

                    if (alreadythere2 == true) {
                        System.out.println("ERROR: The coordination " + z1 + z2 + " is already ocupied. Try again! ");
                    }

                    if (badformat2 == true) {
                        System.out.println("ERROR: You did not enter coordination in the right format. Try again! ");

                    }

                    if (unexistedcoord2 == true) {
                        System.out.print("ERROR: The coordination " + z1 + z2 + " doesn't exist. Try again! ");
                    }

                    try {
                        z = input.nextLine();
                        z1 = z.substring(0, 1).toLowerCase();
                        z2 = z.substring(1);

                        g = "abcdefghijklmnopqrstuvwxyz";
                        first2 = g.indexOf(z1) + 1;
                        second2 = Integer.parseInt(z2);
                    } catch (Exception e) {
                    }

                    alreadythere2 = (player1Coord.contains(z) || player2Coord.contains(z));
                    badformat2 = (SettingTheBoard.isInteger(z1) == true || SettingTheBoard.isInteger(z2) == false);
                    unexistedcoord2 = (first2 > q || second2 > q);
                }

                // ASSIGNING LETTER
                int ll = g.indexOf(z1);
                int hh = 1 + 2 * ll;
                letters2[d] = hh;

                // ASSIGNING NUMBER
                int kk = Integer.parseInt(z2);
                int rr = x - (2 * kk);
                numbers2[d] = rr;

                // ASSIGNING LETTER
                int l2 = g.indexOf(z1) + 1;

                // ASSIGNING NUMBER
                int k2 = Integer.parseInt(z2);

                String str2 = Integer.toString(l2) + Integer.toString(k2);

                int coord2 = Integer.parseInt(str2);

                p2code.add(coord2);

                p2code.sort(null);

                player2Coord.add(z);
                p2n.add(rr);
                p2l.add(hh);

                ///////////////////////////////
                //////// MAKING THE BOARD
                ////////////////////////////
                System.out.println("");

                SettingTheBoard.letters(x);

                System.out.println("");

                for (int i = 0; i < x; i++) {

                    for (int j = -1; j < x; j++) {

                        if (i % 2 == 0 && j != -1 || j % 2 == 0) {
                            System.out.print("* ");
                        } else if (j == -1 && i % 2 == 1) {
                            int e = (i + 1) / 2;
                            int ee = q + 1 - e;
                            if (ee > 9) {
                                System.out.print(ee);
                            } else {
                                System.out.print(ee + " ");
                            }
                        } else if (i == numbers[0] && j == letters[0] || i == numbers[1] && j == letters[1] || i == numbers[2] && j == letters[2] || i == numbers[3] && j == letters[3] || i == numbers[4] && j == letters[4] || i == numbers[5] && j == letters[5] || i == numbers[6] && j == letters[6] || i == numbers[7] && j == letters[7] || i == numbers[8] && j == letters[8] || i == numbers[9] && j == letters[9] || i == numbers[10] && j == letters[10] || i == numbers[11] && j == letters[11] || i == numbers[12] && j == letters[12] || i == numbers[13] && j == letters[13] || i == numbers[14] && j == letters[14] || i == numbers[15] && j == letters[15] || i == numbers[16] && j == letters[16] || i == numbers[17] && j == letters[17] || i == numbers[18] && j == letters[18] || i == numbers[19] && j == letters[19] || i == numbers[20] && j == letters[20] || i == numbers[21] && j == letters[21] || i == numbers[22] && j == letters[22] || i == numbers[23] && j == letters[23] || i == numbers[24] && j == letters[24] || i == numbers[25] && j == letters[25] || i == numbers[26] && j == letters[26] || i == numbers[27] && j == letters[27] || i == numbers[28] && j == letters[28] || i == numbers[29] && j == letters[29] || i == numbers[30] && j == letters[30] || i == numbers[31] && j == letters[32]) {
                            System.out.print(c1 + " ");
                        } else if (i == numbers2[0] && j == letters2[0] || i == numbers2[1] && j == letters2[1] || i == numbers2[2] && j == letters2[2] || i == numbers2[3] && j == letters2[3] || i == numbers2[4] && j == letters2[4] || i == numbers2[5] && j == letters2[5] || i == numbers2[6] && j == letters2[6] || i == numbers2[7] && j == letters2[7] || i == numbers2[8] && j == letters2[8] || i == numbers2[9] && j == letters2[9] || i == numbers2[10] && j == letters2[10] || i == numbers2[11] && j == letters2[11] || i == numbers2[12] && j == letters2[12] || i == numbers2[13] && j == letters2[13] || i == numbers2[14] && j == letters2[14] || i == numbers2[15] && j == letters2[15] || i == numbers2[16] && j == letters2[16] || i == numbers2[17] && j == letters2[17] || i == numbers2[18] && j == letters2[18] || i == numbers2[19] && j == letters2[19] || i == numbers2[20] && j == letters2[20] || i == numbers2[21] && j == letters2[21] || i == numbers2[22] && j == letters2[22] || i == numbers2[23] && j == letters2[23] || i == numbers2[24] && j == letters2[24] || i == numbers2[25] && j == letters2[25] || i == numbers2[26] && j == letters2[26] || i == numbers2[27] && j == letters2[27] || i == numbers2[28] && j == letters2[28] || i == numbers2[29] && j == letters2[29] || i == numbers2[30] && j == letters2[30] || i == numbers2[31] && j == letters2[32]) {
                            System.out.print(c2 + " ");
                        } else {
                            System.out.print("  ");
                        }
                    }

                    SettingTheBoard.numbers(i, q);

                    System.out.println("");
                }

                SettingTheBoard.letters(x);

                System.out.println("");
                System.out.println("");
            }

            //////////////////////////////////
            ////// EVALUATION OF THE WINNER
            ///////////////////////////////
            int quit2 = 0;

            if (n == 2) {
                for (int i = 0; i < d; i++) {
                    int gg = p2code.get(i);
                    boolean b1 = p2code.contains(gg + 1);
                    boolean b2 = p2code.contains(gg + 9);
                    boolean b3 = p2code.contains(gg + 10);
                    boolean b4 = p2code.contains(gg + 11);

                    if (b1 || b2 || b3 || b4) {
                        System.out.println("--------------------------------------------------");
                        System.out.println(p2 + " won. Congratulation!!!");
                        System.out.println("--------------------------------------------------");

                        quit2++;
                        d = 500;
                        break;
                    }
                }
            }

            if (n == 3) {

                for (int i = 0; i < d; i++) {
                    int gg = p2code.get(i);
                    boolean b1 = p2code.contains(gg + 1) && p2code.contains(gg + 2);
                    boolean b2 = p2code.contains(gg + 9) && p2code.contains(gg + 18);
                    boolean b3 = p2code.contains(gg + 10) && p2code.contains(gg + 20);
                    boolean b4 = p2code.contains(gg + 11) && p2code.contains(gg + 22);

                    if (b1 || b2 || b3 || b4) {
                        System.out.println("--------------------------------------------------");
                        System.out.println(p2 + " won. Congratulation!!!");
                        System.out.println("--------------------------------------------------");

                        quit2++;
                        d = 500;
                        break;
                    }
                }

            }

            if (n == 4) {
                for (int i = 0; i < d; i++) {
                    int gg = p2code.get(i);
                    boolean b1 = p2code.contains(gg + 1) && p2code.contains(gg + 2) && p2code.contains(gg + 3);
                    boolean b2 = p2code.contains(gg + 9) && p2code.contains(gg + 18) && p2code.contains(gg + 27);
                    boolean b3 = p2code.contains(gg + 10) && p2code.contains(gg + 20) && p2code.contains(gg + 30);
                    boolean b4 = p2code.contains(gg + 11) && p2code.contains(gg + 22) && p2code.contains(gg + 33);

                    if (b1 || b2 || b3 || b4) {
                        System.out.println("--------------------------------------------------");
                        System.out.println(p2 + " won. Congratulation!!!");
                        System.out.println("--------------------------------------------------");

                        quit2++;
                        d = 500;
                        break;
                    }
                }
            }

            if (n == 5) {
                for (int i = 0; i < d; i++) {
                    int gg = p2code.get(i);
                    boolean b1 = p2code.contains(gg + 1) && p2code.contains(gg + 2) && p2code.contains(gg + 3) && p2code.contains(gg + 4);
                    boolean b2 = p2code.contains(gg + 9) && p2code.contains(gg + 18) && p2code.contains(gg + 27) && p2code.contains(gg + 36);
                    boolean b3 = p2code.contains(gg + 10) && p2code.contains(gg + 20) && p2code.contains(gg + 30) && p2code.contains(gg + 40);
                    boolean b4 = p2code.contains(gg + 11) && p2code.contains(gg + 22) && p2code.contains(gg + 33) && p2code.contains(gg + 44);

                    if (b1 || b2 || b3 || b4) {
                        System.out.println("--------------------------------------------------");
                        System.out.println(p1 + " won. Congratulation!!!");
                        System.out.println("--------------------------------------------------");

                        quit2++;
                        d = 500;
                        break;
                    }
                }
            }

            if (quit2 > 0) {
                break;
            }

        }
    }
}
