import React from "react";
import ReactDOM from "react-dom";
import "./index.css";

class AddMessageForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = { msg: "", reply_to: "" };

    this.handleChange = this.handleChange.bind(this);
    this.handleChangeReplyTo = this.handleChangeReplyTo.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({ msg: event.target.value });
  }
  handleChangeReplyTo(event) {
    this.setState({ reply_to: event.target.value });
  }
  resetState() {
    this.setState({ msg: "" });
    this.setState({ reply_to: "" });
  }

  async handleSubmit(event) {
    event.preventDefault(); //this needs to be first line so we dont refresh on post
    let url = "http://127.0.0.1:8000/sms/".concat(this.state.reply_to);
    await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=utf-8",
      },
      body: JSON.stringify({ message: this.state.msg }),
    });
    this.props.update_msg(this.state.reply_to);
    this.resetState();
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <label>
          Message
          <input
            type="text"
            value={this.state.msg}
            onChange={this.handleChange}
          />
        </label>
        <label>
          To (optional)
          <input
            type="number"
            value={this.state.reply_to}
            onChange={this.handleChangeReplyTo}
          />
        </label>
        <input type="submit" value="Submit" />
      </form>
    );
  }
}

function MessageList(props) {
  const msgs = props.display_msg;
  let listMsg = msgs.map((msg) => (
    <li key={msg.id}>
      ID: {msg.id} We try a {msg.method} to {msg.endpoint} with text
      {msg.message}
    </li>
  ));
  return (
    <div>
      <h1>Look at the messages</h1>
      <ul>{listMsg}</ul>
    </div>
  );
}

function Replies(props) {
  // let listMsg = props.display_replies.replies.map((msg) => (
  //   <li key={msg.id}>
  //     Replies to message {msg.id} - {msg.message}: {msg.replies}
  //   </li>
  // ));
  // let reply_id = "";
  // if (props.display_replies.id) {
  //   let replies = props.display_replies.replies;
  //   let reply_id = props.display_replies.id;
  //   let msg = props.display_replies.message;
  //   console.log(reply_id, msg, replies);
  // } else {
  //   console.log("NO NO");
  // }
  return (
    <div>
      <h1>Replies to message {props.display_replies.id}</h1>
      <p>OG msg: {props.display_replies.message}</p>
      <ul>
        {props.display_replies.replies.map((reply) => (
          <li>{reply.message}</li>
        ))}
      </ul>
    </div>
  );
}

class Messages extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      messages: [],
      replies: {
        id: "",
        message: "",
        replies: [],
      },
    };
    this.get_messages = this.get_messages.bind(this); // so it can be called from child
  }

  componentDidMount() {
    this.get_messages();
  }

  // we have no response validation (on error, we just dont do anything)
  async get_replies(reply_id) {
    let url = "http://127.0.0.1:8000/sms/" + reply_id;
    const response = await fetch(url);
    const msgs = await response.json();
    if (msgs) {
      this.setState({ replies: msgs });
    }
  }

  async get_messages(o) {
    if (o) {
      // validate is an int
      this.get_replies(o);
    }
    const url = "http://127.0.0.1:8000/sms/?limit=30";
    const response = await fetch(url);
    const msgs = await response.json();
    this.setState({ messages: msgs });
  }

  render() {
    return (
      <div>
        <h1>Say what you want</h1>
        <AddMessageForm update_msg={this.get_messages} />
        <div className="row">
          <div className="column">
            <MessageList display_msg={this.state.messages} />
          </div>
          <div className="column">
            <Replies display_replies={this.state.replies} />
          </div>
        </div>
      </div>
    );
  }
}

// ========================================

ReactDOM.render(<Messages />, document.getElementById("root"));
