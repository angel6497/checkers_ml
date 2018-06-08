import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.geom.RoundRectangle2D;

import java.io.*;
import java.util.LinkedList;


@SuppressWarnings("serial")
public class GamePage extends JFrame implements WindowListener {
   
    //******* ATTRIBUTES *******
    private int ppid;   // Parent process ID
    private LinkedList<String> buffer = new LinkedList<String>();
    
    // GUI Components
    private BoardPanel board;
    private JPanel statusPanel;
    private JLabel statusMessage;

    // Interprocess communiaction components
    private BufferedReader input;


    
    // Main method
    public static void main(String[] args) throws Exception {

        GamePage frame = new GamePage();
        frame.setVisible(true);

        // Start interprocess communication.
        frame.startInterprocessCommunication();

    }

    // Constructor
    public GamePage() {

        // Init GUI components.

        board = new BoardPanel(this);
        initComponents();

        // Init interprocess communication components.
        input = new BufferedReader(new InputStreamReader(System.in));

    }

    // Init method
    private void initComponents() {
        
        // Set basic values on the JFrame.
        setSize(660, 705);
        setResizable(false);

        // Set window behaviour values.
        setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
        addWindowListener(this);

        // Set initial location.
        Dimension dim = Toolkit.getDefaultToolkit().getScreenSize();
        setLocation(dim.width / 2 - this.getSize().width / 2, dim.height / 2 - this.getSize().height / 2);
        
        // Set layout manager and add components. 
        setLayout(new BorderLayout());

        // Initialize status message components.
        statusPanel = new JPanel();
        statusPanel.setBackground(new Color(64, 64, 64));

        statusMessage = new JLabel("New Game");
        statusMessage.setFont( new Font(Font.SANS_SERIF, Font.PLAIN, 18) );
        statusMessage.setForeground(Color.WHITE);

        statusPanel.add(statusMessage);
        add(statusPanel, BorderLayout.PAGE_START);
        add(board, BorderLayout.CENTER);

    }



    //******* INTERPROCESS COMMUNICATION *******
    
    public void startInterprocessCommunication() throws Exception {

        while(true) {
            try {
                String textCommand = input.readLine();
                String[] commandArray = textCommand.split(" ");

                for (int i = 0; i < commandArray.length; i++) {
                    buffer.add(commandArray[i]);
                }

                switch( buffer.remove() ) {

                    case "set_ppid":
                        int ppid = Integer.parseInt(buffer.remove());
                        this.ppid = ppid;
                        break;

                    case "set_status":
                        String statusMsg = "";
                        while( !buffer.peek().equals("EOM") ) {
                            statusMsg += " " + buffer.remove();
                        }

                        buffer.remove();
                        
                        if (! statusMessage.getText().equals(statusMsg) ) { 
                            changeStatus(statusMsg);
                        }
                        break;

                    case "display":
                        int[][] boardState = new int[8][8];

                        for(int row = 0; row < 8; row++) {
                            for(int col = 0; col < 8; col++) {
                                int tileValue = Integer.parseInt( buffer.remove() );
                                boardState[row][col] = tileValue;
                            }
                        }

                        board.displayBoardState(boardState);
                        break;

                    case "get_move": 
                        int[] move = null;

                        board.resetMoveSelection();
                        board.getMove( buffer.remove() );

                        while(move == null) {
                            Thread.sleep(50);
                            move = board.getSelectedMove();
                        }

                        String textMove;
                        textMove = move[0] + " " + move[1] + " " + move[2] + " " + move[3];

                        System.out.println("SELECTED_MOVE: " + textMove);
                        break;

                    case "popup":
                        String msg = "";
                        while( !buffer.peek().equals("EOM") ) {
                            msg += " " + buffer.remove();
                        }

                        buffer.remove();

                        JOptionPane.showMessageDialog(null, 
                                                      msg, 
                                                      "Illegal Move", 
                                                      JOptionPane.PLAIN_MESSAGE);
                        break;

                    case "game_over":
                        String gameResult = buffer.remove();
                        String winner = "";
                        if (gameResult.equals("black")) {
                            winner = "Black Player";
                        } else if (gameResult.equals("white")) {
                            winner = "White Player";
                        } else if (gameResult.equals("tie")) {
                            winner = "";
                        }

                        JLabel gameOverMsg;
                        if (!winner.isEmpty()) {
                            gameOverMsg = new JLabel(winner + " wins!", JLabel.CENTER);
                        } else { 
                            gameOverMsg = new JLabel("It is a tie!", JLabel.CENTER);
                        }

                        gameOverMsg.setFont( gameOverMsg.getFont().deriveFont(28) );
                        Object[] options = {"Exit Game", "Play Again"};
                        
                        int response = JOptionPane.showOptionDialog(null,
                                                                    gameOverMsg, 
                                                                    "Game Over",
                                                                    JOptionPane.YES_NO_OPTION, 
                                                                    JOptionPane.PLAIN_MESSAGE, 
                                                                    null, 
                                                                    options, 
                                                                    options[1]);

                        System.out.println("RESPONSE: " + response);
                        break;

                }
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }

    }



    //******* PRIVATE METHODS *******

    private void killParentProcess() {
        String killCmd = "kill " + ppid;
        try {
            Runtime.getRuntime().exec(killCmd);
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
    
    // Animates the change of status.
    private void changeStatus(String msg) {
    
        try{
           for (int i = 255; i > 64; i = i - 2) {
               statusMessage.setForeground( new Color(i, i, i) );
               Thread.sleep(5);
           }

           statusMessage.setText(msg);

           for (int i = 64; i < 255; i = i + 2) {
               statusMessage.setForeground( new Color(i, i, i) );
               Thread.sleep(5);
           }
        } catch (InterruptedException ex) {
            ex.printStackTrace();
        }

    }



    //******* WINDOW LISTENER METHODS *******
    
    public void windowClosing(WindowEvent ev) {
        killParentProcess();
        System.exit(0);
    }

    public void windowClosed(WindowEvent ev) {}
    public void windowActivated(WindowEvent ev) {}
    public void windowDeactivated(WindowEvent ev) {}
    public void windowDeiconified(WindowEvent ev) {}
    public void windowIconified(WindowEvent ev) {}
    public void windowOpened(WindowEvent ev) {}
    

}
