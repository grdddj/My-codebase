/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package javaapplication85;

import java.util.Scanner;

/**
 *
 * @author Jirka
 */
public class SettingTheBoard {
 
    
    public static void letters(int a) {
        for (int v = -1; v < a; v++) {
        String g = "abcdefghijklmnopqrstuvwxyz";
        
        
        if (v % 2 ==1) {
            int e = (v + 1)/2 - 1;
            char ee = g.charAt(e);
            System.out.print(ee + " " );
        }
        else {
            System.out.print("  ");
        }
            
           
    }
    } 
    
    
    
        public static void numbers(int b, int q) {
          if (b % 2 == 1) {
              int e = (b + 1)/2;
             int ee = q + 1 - e;
                if (ee > 9){
              System.out.print( ee );
             }
             else {
                 System.out.print( ee + " ");
             }
          }  
        }
    
    public static boolean isInteger(String s) {
    try {
        Integer.parseInt(s);
        return true;
    }
    catch(Exception e ) {
        return false;
    }
}

        
    public static void boardsetup() {
      
         Scanner input = new Scanner(System.in);
        System.out.print("Please enter the size of the board: ");
        
        int q = input.nextInt();
        
       int y = 2*q;
        
        int x = (2*y + 1);
        
        SettingTheBoard.letters(q);
        
        
        System.out.println("");
        
        for (int i = 0; i < x; i++) {
            for (int j = 0; j < x; j++) {
 
                 if (i % 4 == 0 || j % 4 == 0) {
                    System.out.print("* ");
                }
                else {
                    System.out.print("  ");
                }
            }
            
            SettingTheBoard.numbers(i, q);
            
            System.out.println("");
        }
        
         SettingTheBoard.letters(q);       
    

}
}