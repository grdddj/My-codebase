pragma solidity ^0.4.25;

contract Crowdfunding {

    Project[] public projects; // array of all project structs
    mapping(uint => mapping(address => uint)) public contribution; // store how much each user funded to what project

    event NewProject(uint id, address owner, string name, uint goal, uint endTime);
    event Withdrawal(uint id, uint amount);

    struct Project {
        address owner;
        string name;
        uint weiGoal; 
        uint endTime;
        uint received;
        bool finished;
    }

    function createProject(string _name, uint _weiAmount, uint _duration) public {
        // create a new Project struct and push it into projects array
        // also get an id, that will be used in event
        uint id = projects.push(Project(msg.sender, _name, _weiAmount, now + _duration, 0, false)) - 1;

        emit NewProject(id, msg.sender, _name, _weiAmount, now + _duration); // emit event
    }

    function fundProject(uint _id) public payable {
        require(now < projects[_id].endTime); // the project has not expired yet
        require(projects[_id].finished == false); // project has not been completely funded yet
        projects[_id].received += msg.value; // add value to project funds
        contribution[_id][msg.sender] += msg.value; // add value to the specific user
        if (projects[_id].received > projects[_id].weiGoal) { //when more than enough is collected, finish the crowdfunding
            projects[_id].finished = true;
        }
    }

    function withdrawFunds(uint _id) public {
        require(msg.sender == projects[_id].owner); // only owner of the project can call it
        require(projects[_id].finished == true); // the project has reached the goal
        uint amount = projects[_id].received; // storing the crowdfunded value before setting it to zero
        projects[_id].received = 0; // setting the value to zero before sending the funds
        msg.sender.transfer(amount); // transfering the funds to the project's owner
        emit Withdrawal(_id, amount);

    }

     function getRefund(uint _id) public {
         require(now > projects[_id].endTime); // time has already passed
         require(projects[_id].finished == false); // project did not receive enough money
         require(contribution[_id][msg.sender] > 0); // msg.sender must have contributed
         uint amount = contribution[_id][msg.sender]; // getting the amount before setting it to zero
         contribution[_id][msg.sender] = 0; // set this contribution to zero before sending money back
         msg.sender.transfer(amount); // refunding the money to the funder
     }

     function getNumberOfProjects() public view returns (uint) {
        return projects.length;
     }
}