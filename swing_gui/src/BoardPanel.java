import javax.swing.*;
import java.awt.*;
import java.awt.List;
import java.awt.event.*;
import java.awt.geom.*;

import java.util.*;


@SuppressWarnings("serial")
public class BoardPanel extends JPanel {

    //******* ATTRIBUTES *******

    // Constants
    private static final int LENGTH = 80;
    private static final int HORIZONTAL_RECTANGLES = 8;
    private static final int VERTICAL_RECTANGLES = 8;
    private static final int OFFSET = 10;

    private GamePage frame;
    private int[][] boardState = new int[8][8];
    private BoardMode mode = BoardMode.IDLE;
    private int[] selectedPiece = null;
    private int[] selectedMove = null;


    // Constructor
    public BoardPanel(GamePage gp) {

        frame = gp;
       
        // Initialize board status.
        for(int col = 0; col < 8; col++) {
            for(int row = 0; row < 8; row++) {
                if ((col % 2 == 0 && row % 2 == 0) || (col % 2 == 1 && row % 2 == 1)) { // If tile is black.
                    if (row <= 2){
                        boardState[row][col] = 1;  // Fill the upper half with black pawns.
                    } else if (row >= 5) {
                        boardState[row][col] = -1; // Fill the lower half with white pawns.
                    }
                }
            }
        }
         
        addMouseListener(new BoardMouseListener());

    }

    // This method must be implemented in order
    // for the JPanel to do the painting. 
    public void paintComponent(Graphics g) { 
        
        super.paintComponent(g);

        Graphics2D g2d = (Graphics2D)g;
        RenderingHints rh = new RenderingHints(RenderingHints.KEY_ANTIALIASING,
                                               RenderingHints.VALUE_ANTIALIAS_ON);
        g2d.setRenderingHints(rh);

        paintTiles(g2d);

        for(int col = 0; col < 8; col++) {
            for(int row = 0; row < 8; row++) {
                switch(boardState[row][col]) {
                    case 1:   paintBlackPiece(col, row, "pawn", false, g2d); // Black pawn
                              break;
                    case 10:  paintBlackPiece(col, row, "pawn", true, g2d);  // Black selected pawn
                              break;
                    case 3:   paintBlackPiece(col, row, "king", false, g2d); // Black king
                              break;
                    case 30:  paintBlackPiece(col, row, "king", true, g2d);  // Black selected king
                              break;
                    case -1:  paintWhitePiece(col, row, "pawn", false, g2d); // White pawn
                              break;
                    case -10: paintWhitePiece(col, row, "pawn", true, g2d);  // White selected pawn
                              break;
                    case -3:  paintWhitePiece(col, row, "king", false, g2d); // White king
                              break;
                    case -30: paintWhitePiece(col, row, "king", true, g2d);  // White selected king
                              break;
                }
            }
        }

    }



    //******* INTERFACE METHODS *******
    
    public void displayBoardState(int[][] pieces) {
        
        boardState = pieces;
        repaint();

    }

    public void getMove(String color) {
        
        if (color.equals("black")) {
            mode = BoardMode.GET_BLACK_MOVE;
        } else if (color.equals("white")) { 
            mode = BoardMode.GET_WHITE_MOVE;
        }

    }

    public void resetMoveSelection() {
        
        selectedPiece = null;
        selectedMove  = null;

    }

    public int[] getSelectedMove() {

        return selectedMove;

    }



    //******* PRIVATE METHODS *******

    // Paint a 8x8 grid of alternating black and white tiles.
    private void paintTiles(Graphics2D g2d) {
        
        // Frame around tiles.
        g2d.setColor(Color.DARK_GRAY);
        g2d.fill(new Rectangle2D.Float(0, 0, 660, 682));

        // Initialize the rectangles list to cover the whole board
        for (int row = 0; row < HORIZONTAL_RECTANGLES; row++) {
            for (int col = 0; col < VERTICAL_RECTANGLES; col++) {
                Rectangle2D r = new Rectangle2D.Float(OFFSET + (LENGTH * col), (LENGTH * row), LENGTH, LENGTH);
                
                if ((row % 2 == 0 && col % 2 == 0) || (row % 2 == 1 && col % 2 == 1)) {
                    g2d.setColor(Color.black);
                } else {
                    g2d.setColor(Color.white);
                }

                g2d.fill(r);
            }
        }

    }
    
    // Paint a black piece in the given position.
    private void paintBlackPiece(int xt, int yt, String kind, boolean isSelected, Graphics2D g2d) {

        int[] pixelCoordinates = tileToPixel(xt, yt);
        int x = pixelCoordinates[0];
        int y = pixelCoordinates[1];
        Color secondaryColor = new Color(173, 30, 8);

        // Paint blue ring to show that piece has been selected.
        if (isSelected) {
            g2d.setColor(secondaryColor);
            g2d.fill(new Ellipse2D.Float(x - 1, y - 1, LENGTH, LENGTH));
        }

        // Paint the piece itself
        g2d.setColor(new Color(67, 67, 67));
        g2d.fill(new Ellipse2D.Float(x - 1 + (OFFSET / 2), y - 1 + (OFFSET / 2), LENGTH - OFFSET, LENGTH - OFFSET));
        // Make red ring around black piece to make it visible on top of black tiles.
        g2d.setColor(new Color(173, 30, 8));

        if (kind.equals("king")) {
            g2d.setColor(secondaryColor);
            g2d.fill(new Ellipse2D.Float(x + 29, y + 29, 20, 20));
        }

    }

    // Paint a white piece in the given location.
    private void paintWhitePiece(int xt, int yt, String kind, boolean isSelected, Graphics2D g2d) {

        int[] pixelCoordinates = tileToPixel(xt, yt);
        int x = pixelCoordinates[0];
        int y = pixelCoordinates[1];
        Color secondaryColor = new Color(6, 82, 168);

        // Paint blue ring to show that piece has been selected.
        if (isSelected) {
            g2d.setColor(secondaryColor);
            g2d.fill(new Ellipse2D.Float(x - 1, y - 1, LENGTH, LENGTH));
        }

        // Paint the piece itself
        g2d.setColor(Color.WHITE);
        g2d.fill(new Ellipse2D.Float(x - 1 + (OFFSET / 2), y - 1 + (OFFSET / 2), LENGTH - OFFSET, LENGTH - OFFSET));

        if (kind.equals("king")) {
            g2d.setColor(secondaryColor);
            g2d.fill(new Ellipse2D.Float(x + 29, y + 29, 20, 20));
        }

    }

    // Converts x and y pixel coordinates into tile coordinates.
    private int[] pixelToTile(int xp, int yp) {

        int xt = (xp - 1 - OFFSET) / LENGTH;
        int yt = (yp - 1 - OFFSET) / LENGTH;
        
        int[] tileCoordinates = {xt, yt};
        
        return tileCoordinates;

    }

    // Converts x and y tile coordinates into pixel coordinates.
    private int[] tileToPixel(int xt, int yt) {
       
        int xp = (xt * LENGTH) + OFFSET + 1;
        int yp = (yt * LENGTH) + 1;

        int[] pixelCoordinates = {xp, yp};

        return pixelCoordinates;
        
    }

        

    //******* INNER LISTENER CLASS *******

    class BoardMouseListener implements MouseListener {

        public void mouseClicked(MouseEvent ev) {
            int x = ev.getX();
            int y = ev.getY(); 

            int[] tc = pixelToTile(x, y);
            int selectedTile = boardState[tc[1]][tc[0]];

            switch (mode) {
                
                case GET_BLACK_MOVE: if (selectedPiece != null) {
                                        selectedMove = new int[4];
                                        selectedMove[0] = selectedPiece[0];
                                        selectedMove[1] = selectedPiece[1];
                                        selectedMove[2] = tc[0];
                                        selectedMove[3] = tc[1];
                                     } else if (selectedTile > 0) {
                                        selectedPiece = new int[2];
                                        selectedPiece[0] = tc[0];
                                        selectedPiece[1] = tc[1];
                                        boardState[tc[1]][tc[0]] *= 10;
                                        repaint();
                                     }
                                     break;

                case GET_WHITE_MOVE: if (selectedPiece != null) {
                                        selectedMove = new int[4];
                                        selectedMove[0] = selectedPiece[0];
                                        selectedMove[1] = selectedPiece[1];
                                        selectedMove[2] = tc[0];
                                        selectedMove[3] = tc[1];
                                     } else if (selectedTile < 0) {
                                        selectedPiece = new int[2];
                                        selectedPiece[0] = tc[0];
                                        selectedPiece[1] = tc[1];
                                        boardState[tc[1]][tc[0]] *= 10;
                                        repaint();
                                     }
                                     break;

            }
        }

        // Mouse Listener interface required the implementation of these methods.
        public void mousePressed(MouseEvent ev) {}
        public void mouseReleased(MouseEvent ev) {}
        public void mouseEntered(MouseEvent ev) {}
        public void mouseExited(MouseEvent ev) {}

    }



    //******* CUSTOM ENUM TYPE *******

    private enum BoardMode {
        IDLE,
        GET_WHITE_MOVE,
        GET_BLACK_MOVE
    }

}
