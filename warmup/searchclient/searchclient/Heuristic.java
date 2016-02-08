package searchclient;

import java.util.Comparator;

public abstract class Heuristic implements Comparator< Node > {

	public Node initialState;
	public Heuristic(Node initialState) {
		this.initialState = initialState;
	}

	public int compare( Node n1, Node n2 ) {
		return f( n1 ) - f( n2 );
	}

	public int h( Node n ) {
    return manhattenDistance(n);
	}

  /**
   *  Returns the Manhattan distance for all box to their goal states.
   */
  private int manhattenDistance(Node n) {
    int minDistance, // min distance for each box
        sum = 0;     // complete sum for all boxes to min goal

    // find box first (they are uppercased)
    for ( int row = 1; row < n.MAX_ROW - 1; row++ ) {
      for ( int col = 1; col < n.MAX_COLUMN - 1; col++ ) {
        char b = n.boxes[row][col];
				if ( 'A' <= b && b <= 'Z' ) {
          minDistance = Integer.MAX_VALUE;
          // lowercase box letter for comparison
          b = Character.toLowerCase( b );

          // now find ALL corresponding goal states
          for ( int i = 1; i < n.MAX_ROW - 1; i++) {
            for ( int j = 1; j < n.MAX_COLUMN - 1; j++) {
              char g = n.goals[i][j];
              if ( 'a' <= g && g <= 'z' && b == g) {
                int r = row - i;
                int c = col - j;

                minDistance = Math.min( (Math.abs(r) + Math.abs(c)), minDistance );
              }
            }
          }
          sum += minDistance; // update complete sum
        }
      }
    }
    return sum;
  }

	public abstract int f( Node n );

	public static class AStar extends Heuristic {
		public AStar(Node initialState) {
			super( initialState );
		}

		public int f( Node n ) {
			return n.g() + h( n );
		}

		public String toString() {
			return "A* evaluation";
		}
	}

	public static class WeightedAStar extends Heuristic {
		private int W;

		public WeightedAStar(Node initialState) {
			super( initialState );
			W = 5; // You're welcome to test this out with different values, but for the reporting part you must at least indicate benchmarks for W = 5
		}

		public int f( Node n ) {
			return n.g() + W * h( n );
		}

		public String toString() {
			return String.format( "WA*(%d) evaluation", W );
		}
	}

	public static class Greedy extends Heuristic {

		public Greedy(Node initialState) {
			super( initialState );
		}

		public int f( Node n ) {
			return h( n );
		}

		public String toString() {
			return "Greedy evaluation";
		}
	}
}
