import React, { Component } from 'react';
import { Container, Button } from 'reactstrap';
import Title from './JumboTron'
import Steps from './Step'

const goToLogin = () => {
  window.location.href = 'http://192.168.86.26:8000/login';
};

class App extends Component {

  render() {
    return (
      <div>
        <Title/>
          <Container>
            <Steps/>
          </Container>
      </div>


    );
  }
}

export default App;
