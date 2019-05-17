var HumPlayer = function (name) {


	var match = null;
    var position = null;
    var current_game = null;
    var player_key = null;
    var CARD_MARGIN = -75;
    var CARD_WIDTH = 150;
  	var PASSING_NUMBER = 3;

  	var norths_points = 0;
  	var easts_points = 0;
  	var wests_points = 0;
  	var souths_points = 0;

  	var foo = 0;

  	var mode = "passing";


    var cardsSelected=0;

    var trickArr = {North: '',East:'',South: '',West: ''};



    

    this.setupMatch = function (hearts_match, pos) {
		match = hearts_match;
		position = pos;
		//foo(hearts_match, Hearts.east);
	}

    this.getName = function () {	return name; }

    this.setName = function (_name) {name = _name; }

    function showCardImages(cards) {
    	$("#hand").empty();

    	for (i = 0; i < cards.length; i++) { 
    		var cardString = "Playing Cards/"+cards[i]+".png";

	    	var curId = "card" + i;	
	    	var $cur = $('<img class="cardSpecs">');
	    	$cur.attr('src',cardString);
	    	$cur.attr('id', cards[i].getRank()+"_of_"+getSuitName(cards[i].getSuit()));	

			$cur.data('suit',cards[i].getSuit());
			$cur.data('rank',cards[i].getRank());

			$cur.data('cardInfo', cardString);
			$cur.data('card',cards[i]);

			$("#hand").append($cur);
			$cur.click( handleCardClick );
		}
    }

    function getSuitName(num) {
    	if( num == 1 ){
    		return "spades";
    	}
    	if( num == 2 ){
    		return "diamonds";
    	}
    	if( num == 3 ){
    		return "clubs";
    	}
    	if( num == 0 ){
    		return "hearts";
    	}
    }
    
    function displayHand() {
    	var cards = current_game.getHand(player_key).getUnplayedCards(player_key);

		cards = orderCards(cards);
		showCardImages(cards);
    }

	function handleCardClick() {
		if( mode == "passing"){
			passingCardSelection($(this));
		} else {
			var $cur = $(this);
			var card = $cur.data('card');
			if(inPlayableCards(card) >= 0){
				var playable_cards = current_game.getHand(player_key).getPlayableCards(player_key);

				current_game.playCard(playable_cards[inPlayableCards(card)], player_key);
				displayHand();
			} else {
				setHelperText(" Pick another card, that one is not playable.");
			}
		}
	}
	function passingCardSelection(yo){
		yo.toggleClass('cardSpecs--picked');
	}

	function passCards() {

		var cardsChosen = [];

		$("#hand").find('.cardSpecs--picked').each(function() {
			var $card = $(this);

			cardsChosen.push(new Card($card.data('rank'), $card.data('suit')));
				

		});

		if( cardsChosen.length !== PASSING_NUMBER ) {
			console.log("incorrect number of cards selected");
		}else {
			var str = "";
	    	for (i = 0; i < cardsChosen.length; i++) { 
	    		 str += "Passing the " + cardsChosen[i].getRank() + " of " + getSuitName(cardsChosen[i].getSuit()) +"\n";
	    	}
	    	alert(str);

			current_game.passCards(cardsChosen, player_key);

			//remove passCard button
			$("#table").find("#pcb").remove();

			mode = "playing";

			$("#hand").find('.cardSpecs--picked').each(function() {
			var $card=$(this);
			$card.remove();
			});

			displayHand();
		}}

	function addPassCardButton(){ //pass card button

		$pcdiv = $('<div></div>');
		$pcdiv.attr('id','pcdiv');
		$pcdiv.css('text-align','center');

		$pcb = $('<button type="button">Pass Cards</button>');
		$pcb.attr('id', 'pcb');
		$("#text").append($pcdiv);
		$pcdiv.append($pcb);

		$pcb.click(passCards);
	}


	function playCardHandler(playable_cards) {
		//cards = current_game.getHand(player_key).getUnplayedCards(player_key);
		var pcs = "";
		for( i = 0; i < playable_cards.length; i++ ){



			if(i == 0){
				pcs = "You can play "+ playable_cards[i] +", ";
			} else{
				pcs +=playable_cards[i] +", ";
			}

			
		
			// document.getElementById("'"+playable_cards[i]+"'").addClass('playable');
		}
		$("#myText").empty();
		$("#myText").text(pcs);
		console.log(pcs);
	}

	function inPlayableCards(card){
		var playable_cards = current_game.getHand(player_key).getPlayableCards(player_key);

		for(i = 0; i < playable_cards.length; i++ ){
			if( playable_cards[i] == card ) {
				return i;
			}
		}
		return -1;
	}

	function orderCards(cards){
		suitIndexes= [Card.Suit.SPADE, Card.Suit.DIAMOND, Card.Suit.CLUB, Card.Suit.HEART];

		return cards.sort(function(c1,c2){
			var suit1 = suitIndexes.indexOf(c1.getSuit());
			var suit2 = suitIndexes.indexOf(c2.getSuit());

			if( suit1 !== suit2 ){
				return suit1 - suit2;
			}

			return c1.getRank() - c2.getRank();
		});
	}

	function setHelperText(str){
		var $tb = $('<h3>' + str +'</h3>');
		$tb.css('text-align', 'center');
		$("#text").empty();
		$("#text").append($tb);
	}
	function setLastTrickText(str) {
		var $ltt = $('<h3>' + str +'</h3>');
		$ltt.css('text-align', 'center');
		$("#lastWinnerText").empty();
		$("#lastWinnerText").append($ltt);
	}
    
	function setTable(e){
		var cardString = "Playing Cards/" + "red_joker" + ".png";

    	var $west = $('<img class="cardSpecs">');
    	$west.attr('src', cardString);
    	$west.attr('id', "West");	

		var $south = $('<img class="cardSpecs">');
    	$south.attr('src', cardString);
    	$south.attr('id', "South");	

    	var $east = $('<img class="cardSpecs">');
    	$east.attr('src', cardString); 
    	$east.attr('id', "East");	

		$("#table").empty();
		$("#table").append($west);
		$("#table").append($south);
		$("#table").append($east);
	}

	function findPType(num) {
		if(num == 1 ){
			return "be passing to the left this round";
		}
		if(num == 2 ){
			return "be passing to the right this round";
		}
		if(num == 3 ){
			return "be passing across this round";
		}
		if(num == 4 ){
			return "not be passing this round";
		}
	}
	

	function setLastTrickDisplay(){
		$("#northCol").empty();
		$("#eastCol").empty();
		$("#southCol").empty();
		$("#westCol").empty();

		var cardString = "Playing Cards/" + "red_joker" + ".png";

		var str = "";
		var fullStr = "";
		var $ltText = $('<h2>'+ fullStr +'</h2>');
		
		var $northH =$('<h2>NORTH</h2>');
		$("#northCol").append($northH);
		
		var $eastH =$('<h2>EAST</h2>');
		$("#eastCol").append($eastH);
		
		var $southH =$('<h2>SOUTH</h2>');
		$("#southCol").append($southH);
		
		var $westH =$('<h2>WEST</h2>');
		$("#westCol").append($westH);



		var $northSc =$('<h2>score</h2>');
		$("#northCol").append($northSc);
		$northSc.attr('id', "northSc");

		var $eastSc =$('<h2>score</h2>');
		$("#eastCol").append($eastSc);
		$eastSc.attr('id', "eastSc");

		var $southSc =$('<h2>score</h2>');
		$("#southCol").append($southSc);
		$southSc.attr('id', "southSc");

		var $westSc =$('<h2>score</h2>');
		$("#westCol").append($westSc);
		$westSc.attr('id', "westSc");


		var $north = $('<img class="cardSpecs">');
    	$north.attr('src', cardString);
    	$north.attr('id', "ltNorth");
    	$north.addClass('noHoverMarginChange');


		var $south = $('<img class="cardSpecs">');
    	$south.attr('src', cardString);
    	$south.attr('id', "ltSouth");	
    	$south.addClass('noHoverMarginChange');


		var $east = $('<img class="cardSpecs">');
    	$east.attr('src', cardString); 
    	$east.attr('id', "ltEast");	
    	$east.addClass('noHoverMarginChange');

    	var $west = $('<img class="cardSpecs">');
    	$west.attr('src', cardString);
    	$west.attr('id', "ltWest");	
    	$west.addClass('noHoverMarginChange');

		

		$("#lastTrick").empty();
		$("#lastTrickText").empty();

		$("#northCol").append($north);
		$("#eastCol").append($east);
		$("#southCol").append($south);
		$("#westCol").append($west);
	}



	function displayLastTrick() {
		var ncard = "Playing Cards/" + trickArr['North'] + ".png";
		var ecard = "Playing Cards/" + trickArr['East'] + ".png";
		var scard = "Playing Cards/" + trickArr['South'] + ".png";
		var wcard = "Playing Cards/" + trickArr['West'] + ".png";

		$("#ltNorth").attr('src',ncard);
		$("#ltEast").attr('src',ecard);
		$("#ltSouth").attr('src',scard);
		$("#ltWest").attr('src',wcard);

	}

	function displayScore(scores){
		
		northspoints = scores[Hearts.NORTH];
		eastspoints = scores[Hearts.EAST];
		southspoints = scores[Hearts.SOUTH];
		westspoints = scores[Hearts.WEST];
	
console.log("northspoints" +northspoints);

		document.getElementById("northSc").innerHTML= ""+northspoints;
		document.getElementById("eastSc").innerHTML= ""+eastspoints;
		document.getElementById("southSc").innerHTML= ""+southspoints;
		document.getElementById("westSc").innerHTML= ""+westspoints;

	}


	
    this.setupNextGame = function (game_of_hearts, pkey) {
		document.getElementById("north_player_header").innerHTML=this.getName() + " (North)";
		current_game = game_of_hearts;
		player_key = pkey;
		var that = this;
		



		current_game.registerEventHandler(Hearts.GAME_STARTED_EVENT, function (e) {
			var ptype = findPType(e.getPassType());
			setHelperText("Please select " + PASSING_NUMBER + " cards to pass. Then click Pass Cards.\n You will "+ ptype);
			
			var scores = match.getScoreboard();
			setLastTrickDisplay();
			displayScore(scores);

			console.log(e.toString()); foo++;
		  	if (e.getPassType() != Hearts.PASS_NONE) {
		  		mode = "passing";
				addPassCardButton();
			}
			if( e.getPassType() == Hearts.PASS_NONE){
				alert("No passing this round.");
			}

			displayHand();
			setTable();
			
		});

		current_game.registerEventHandler(Hearts.CARD_PLAYED_EVENT, function(e){
			//console.log("position is "+e.getPosition() + " and they played "+ e.getCard());

			trickArr[e.getPosition()] = e.getCard();
			//console.log(" trickArr at " + e.getPosition() + " is " + trickArr[e.getPosition()]);


			var player_pos = '#'+e.getPosition();
    		var cardString = "Playing Cards/"+e.getCard()+".png";

			$(player_pos).attr('src',cardString);
		});

		current_game.registerEventHandler(Hearts.TRICK_START_EVENT, function (e) {

			console.log("New Trick: starting with " + e.getStartPos());
			setTable();

		    if (e.getStartPos() == position) {
				var playable_cards = current_game.getHand(player_key).getPlayableCards(player_key);

				setHelperText( "You play first. Click on a playable card." );
				
				playCardHandler(playable_cards);
			} else {
				setHelperText( e.getStartPos() + " played first. Now it is your turn." );
			}
		});

		current_game.registerEventHandler(Hearts.TRICK_CONTINUE_EVENT, function (e) {

		    if (e.getNextPos() == position) {
			var playable_cards = current_game.getHand(player_key).getPlayableCards(player_key);
			playCardHandler(playable_cards);
			}		
		});

		current_game.registerEventHandler(Hearts.TRICK_COMPLETE_EVENT, function (e) {
			var prev_trick = e.getTrick();

			displayLastTrick();

			var winnerStr = prev_trick.getWinner() + " won the previous trick.";
			
			var wins = prev_trick.getWinner();
			if(prev_trick.hasPoints()){
				if(wins == "North"){
					norths_points += prev_trick.getPoints();
				}
				if(wins =="East"){
					easts_points += prev_trick.getPoints();
				}
				if(wins =="South"){
					souths_points += prev_trick.getPoints();
				}
				if(wins =="West"){
					wests_points += prev_trick.getPoints();
				}
			}
			
			var scoreArr = match.getScoreboard();
			displayScore(scoreArr);


			console.log(winnerStr);
			setLastTrickText(winnerStr);
		});

		current_game.registerEventHandler(Hearts.GAME_OVER_EVENT, function(e) {
			console.log("GAMEOVER");
		});
    }	
}