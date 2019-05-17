var HeartsMatch = function (player_north, player_east, player_south, player_west, options) {



    this.getPlayerName = function(pos) {
        if (pos == Hearts.NORTH) {
            return player_north.getName();
        } else if (pos == Hearts.EAST) {
            return player_east.getName();
        } else if (pos == Hearts.WEST) {
            return player_west.getName();
        } else if (pos == Hearts.SOUTH) {
            return player_south.getName();
        }
    }

    this.getPlayerByPosition = function(pos) {
        if (pos == Hearts.NORTH) {
            return player_north;
        } else if (pos == Hearts.EAST) {
            return player_east;
        } else if (pos == Hearts.WEST) {
            return player_west;
        } else if (pos == Hearts.SOUTH) {
            return player_south;
        }
    }



}