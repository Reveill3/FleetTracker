import React, { Component } from 'react';
import {ListGroup} from 'reactstrap';
import Equipment from './Equipment';

class Transit extends Component {

  state = {
    pending: false,
    pumps: []
  };

  handleCancelClick = (index) => {
    this.setState((prevState) =>
      prevState.pumps[index].isCancelled = !prevState.pumps[index].isCancelled
    );

    this.setState((prevState) => {
        prevState.pumps.every((equipment) => equipment.isCancelled === false)
          ? prevState.pending = false: prevState.pending = true
      }
    )};


  checkstate = () => console.log(this.state, this.state.pumps.every((equipment) => !equipment.isCancelled));


  canceltransit = () => {};

  retrieveInTransit = () => {
    if (this.state.pending) {
      this.canceltransit();
    } else {
      fetch('http://192.168.86.26:8000/api/v1/transit_list', {mode: 'cors'})
        .then(response => response.json())
        .then(MyJson => MyJson.map((entry, index) =>
          this.pumparray.push(
            {
              unitnumber: entry.unitnumber,
              id: index,
              message: entry.unitnumber + ' was moved to ' + entry.transferto,
              isCancelled: false
            })));
      this.setState({
        ...this.state,
        pumps: this.pumparray
      });
      this.pumparray = [];
    }};



  render() {
    return (
      <ListGroup>
        <Equipment transitequipment={this.state.pumps} cancelClick={this.handleCancelClick}/>
        <button className='btn btn-dark' onClick={this.retrieveInTransit}>
          {this.state.pending ? 'Submit Cancellations': 'Refresh'}
        </button>
      </ListGroup>
    );
  }
}

export default  Transit;