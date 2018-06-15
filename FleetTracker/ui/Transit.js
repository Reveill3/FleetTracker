import React, { Component } from 'react';
import {ListGroup} from 'reactstrap';
import Equipment from './Equipment';

class Transit extends Component {

  state = {
    pumps: [
      {
        number: '53Q-11067',
        inTransit: true,
        message: 'was moved to red crew from blue.'
      },
      {
        number: '53Q-11055',
        inTransit: true,
        message: 'was moved to red crew from blue.'
      },
      {
        number: '53Q-11053',
        inTransit: true,
        message: 'was moved to red crew from blue.'
      }
    ]
  };


  render() {
    return (
    <ListGroup className='col-md'>
      <Equipment transitequipment={this.state.pumps} />
    </ListGroup>
    );
  }
}

export default Transit;