import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import Transit from "./Transit";


let rootid = document.getElementById('root');
let transitid = document.getElementById('transit');


if (rootid) {
  ReactDOM.render(<App />, document.getElementById('root'));
}



if (transitid) {
  ReactDOM.render(<Transit/>, document.getElementById('transit'));
}
