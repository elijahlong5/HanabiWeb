$(document).ready(function () {
    var north = new HumPlayer("Taco Baco");
    var east = new DumbAI("Super man");
    var south = new DumbAI("JZ");
    var west = new DumbAI("Leo the Lion");

    var match = new HeartsMatch(north, east, south, west);

    match.run();
});