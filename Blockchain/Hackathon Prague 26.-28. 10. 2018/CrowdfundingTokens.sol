pragma solidity ^0.4.24;

 // importing ERC20 tokens to be able to manipulate with them
import {StandardToken as ERC20} from "./lib/StandardToken.sol";

 contract CrowdfundingTokens  {

  // address of the (stable) token that will be used in this crowdfunding
   address public token;

    Project[] public projects; // array of all project structs
    mapping(uint => mapping(address => uint)) public contribution; // store how much each user funded to what project

    event NewProject(uint id, address owner, string name, uint goal, uint endTime);
    event Withdrawal(uint id, uint amount);

    struct Project {
        address owner;
        string name;
        uint goal; 
        uint endTime;
        uint received;
        bool finished;
    }

    // assigning specific token address in constructor
    // then this address is unchangeable
    constructor(address _token) public {
      token = _token;
    }

    // helper function to create transfer() capabilities with the ERC20 token
    // function can only be called inside the contract by other functions
    function transfer2(address _to, uint _amount) internal returns (bool) {
        require(ERC20(token).transfer(_to, _amount));
        return true;
    }

    // helper function to create transferFrom() capabilities with the ERC20 token
    // function can only be called inside the contract by other functions
      function transferFrom2(address _from, address _to, uint _amount) internal returns (bool) {
        require(ERC20(token).transferFrom(_from, _to, _amount));
        return true;
    }

      function createProject(string _name, uint _amount, uint _duration) public {
        // create a new Project struct and push it into projects array
        // also get an id, that will be used in event
        uint id = projects.push(Project(msg.sender, _name, _amount, now + _duration, 0, false)) - 1;

        emit NewProject(id, msg.sender, _name, _amount, now + _duration); // emit event
    }


    // function used to send tokens to the specific project
    // approval of _amount tokens need to occur before calling this function
    // _id = project number
    // _amount = number of tokens wanted to send
    function fundProject(uint _id, uint _amount) public {
        require(now < projects[_id].endTime); // the project has not expired yet
        require(projects[_id].finished == false); // project has not been completely funded yet
        projects[_id].received += _amount; // add value to project funds
        contribution[_id][msg.sender] += _amount; // add value to the specific user
        if (projects[_id].received >= projects[_id].goal) { //when enough is collected, finish the crowdfunding
            projects[_id].finished = true;
        }
        transferFrom2(msg.sender, address(this), _amount); // make transfer as a last operation, to avoid reentrancy problems
    }

    // function used to withdraw tokens for the specific project after this has been successfuly finished
    // _id = project number
      function withdrawFunds(uint _id) public {
        require(msg.sender == projects[_id].owner); // only owner of the project can call it
        require(projects[_id].finished == true); // the project has reached the goal
        uint amount = projects[_id].received; // storing the crowdfunded value before setting it to zero
        projects[_id].received = 0; // setting the value to zero before sending the funds
        transfer2(msg.sender, amount); // withdrawing the amount
        emit Withdrawal(_id, amount);
    }

    // function used to get back tokens from the specific project if the goal has not been reached
    // _id = project number
     function getRefund(uint _id) public {
         require(now > projects[_id].endTime); // time has already passed
         require(projects[_id].finished == false); // project did not receive enough money
         require(contribution[_id][msg.sender] > 0); // msg.sender must have contributed
         uint amount = contribution[_id][msg.sender]; // getting the amount before setting it to zero
         contribution[_id][msg.sender] = 0; // set this contribution to zero before sending money back
         transfer2(msg.sender, amount); // refunding the tokens to the funder
     }

     // function used to find out the number of projects (for the purposes of UI)
     function getNumberOfProjects() public view returns (uint) {
        return projects.length;
     }
 }


 