/* Game of Hanabi model object. */

var Hababi = {
    // Player positions
    NORTH : "North",
    EAST : "East",
    SOUTH : "South",
    WEST : "West",

    // Game status constants
    FINISHED : -1,
    REGISTERING_PLAYERS : 0,
    GAME_IN_PROGRESS : 2,

    //last round?



}

var GameOfHanabi = function () {

    /* The makeKey function is used to create
     * keys for each player as they register
     * in order to authenticate player actions */

    var makeKey = function(len) {
        var key = "";
        var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        for (var i=0; i<len; i++) {
            key += possible.charAt(Math.floor(Math.random()*possible.length));
        }
        return key;
    };

    var game_key = makeKey(10);

    var deck = new Deck();
    deck.shuffle();

    var hands



}