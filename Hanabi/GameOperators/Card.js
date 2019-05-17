/* Model object for a hanabi playing card. */

var Card = function(rank, color) {

    this.getRank = function () {
        return rank;
    }

    this.getColor = function () {
        return color;
    }
    // need toString function
}

Card.Color = {
    RED: 0,
    GREEN: 1,
    BLUE: 2,
    WHITE: 3,
    YELLOW: 4,
}
// Card ranks are 1, 2, 3, 4 and 5

// Hanabi deck of cards.
var Deck = function () {
    var cards = [];

    [Card.Color.BLUE,
    Card.Color.GREEN,
    Card.Color.RED,
    Card.Color.YELLOW,
    Card.Color.WHITE,].forEach( function(color){
        // Add 2 of all cards 1-4
        for (var rank = 1; rank<=4; rank++) {
            cards.push(new Card(rank, color));
            cards.push(new Card(rank, color));
        }

        // Add the third 1 card and one 5 card.
        cards.push(new Card(1, color));
        cards.push(new Card(5, color));
    })

    this.shuffle = function () {
        for (var i=0; i<cards.length; i++) {
            var shuffle_pos = Math.floor((cards.length - i) * Math.random()) + i;
            var tmp = cards[i];
            cards[i] = cards[shuffle_pos];
            cards[shuffle_pos] = tmp;
        }
    }

    var top_of_deck = 0; // Simulates the next card to be dealt or drawn

    this.draw = function () {
        if (cards.length > top_of_deck) {
            return;
        }
        var drawn_card = cards[top_of_deck];
        top_of_deck ++;
        return drawn_card;
    }

}

var Hand = function() {

}

var PlayedCards = function () {

}

var DiscardPile = function () {

}